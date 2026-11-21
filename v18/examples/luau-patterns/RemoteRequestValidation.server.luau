--!strict
-- Server-side example: validate client intent against server-owned world state.
--
-- Studio setup:
-- 1. Create ReplicatedStorage.Remotes as a Folder.
-- 2. Add RemoteEvents named RequestAction and ActionResult.
-- 3. Tag collectible BaseParts with CollectionService tag "SampleCollectible".
-- 4. Place this Script in ServerScriptService.
--
-- This example uses a per-server leaderstats value for clarity. Replace
-- ensureSampleCoins/granting with your existing persistent, server-owned economy
-- service before using it in a live experience. Never treat this sample stat as
-- durable player data.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local CollectionService = game:GetService("CollectionService")

local remotes = ReplicatedStorage:WaitForChild("Remotes")
if not remotes:IsA("Folder") then
    error("ReplicatedStorage.Remotes must be a Folder")
end

local requestEventInstance = remotes:WaitForChild("RequestAction")
local resultEventInstance = remotes:WaitForChild("ActionResult")

if not requestEventInstance:IsA("RemoteEvent") then
    error("Remotes.RequestAction must be a RemoteEvent")
end
if not resultEventInstance:IsA("RemoteEvent") then
    error("Remotes.ActionResult must be a RemoteEvent")
end

local requestEvent = requestEventInstance :: RemoteEvent
local resultEvent = resultEventInstance :: RemoteEvent

local ACTION_COLLECT_SAMPLE = "CollectSample"
local COLLECTIBLE_TAG = "SampleCollectible"
local MAX_COLLECTION_DISTANCE = 16
local REWARD_AMOUNT = 5
local COLLECTION_COOLDOWN_SECONDS = 1

local WINDOW_SECONDS = 5
local MAX_REQUESTS_PER_WINDOW = 8
local REQUEST_ID_TTL_SECONDS = 60
local MAX_REMEMBERED_REQUEST_IDS = 64

type RequestWindow = {
    startedAt: number,
    count: number,
}

local requestWindows: {[number]: RequestWindow} = {}
local lastCollectAt: {[number]: number} = {}
local processedRequestIds: {[number]: {[string]: number}} = {}
local collectedByUser: {[number]: {[Instance]: boolean}} = {}

local function allowRequest(player: Player): boolean
    local now = os.clock()
    local userId = player.UserId
    local bucket = requestWindows[userId]

    if bucket == nil or now - bucket.startedAt >= WINDOW_SECONDS then
        requestWindows[userId] = {startedAt = now, count = 1}
        return true
    end

    if bucket.count >= MAX_REQUESTS_PER_WINDOW then
        return false
    end

    bucket.count += 1
    return true
end

local function isValidRequestId(requestId: unknown): boolean
    return typeof(requestId) == "string"
        and #requestId >= 8
        and #requestId <= 64
        and string.match(requestId, "^[%w%-%_]+$") ~= nil
end

local function rememberRequestId(player: Player, requestId: string): boolean
    local now = os.clock()
    local userId = player.UserId
    local requests = processedRequestIds[userId]

    if requests == nil then
        requests = {}
        processedRequestIds[userId] = requests
    end

    -- Expire old IDs so this in-memory replay guard remains bounded.
    for existingId, expiresAt in pairs(requests) do
        if expiresAt <= now then
            requests[existingId] = nil
        end
    end

    if requests[requestId] ~= nil then
        return false
    end

    local count = 0
    local oldestId: string? = nil
    local oldestExpiry = math.huge

    for existingId, expiresAt in pairs(requests) do
        count += 1
        if expiresAt < oldestExpiry then
            oldestExpiry = expiresAt
            oldestId = existingId
        end
    end

    if count >= MAX_REMEMBERED_REQUEST_IDS and oldestId ~= nil then
        requests[oldestId] = nil
    end

    requests[requestId] = now + REQUEST_ID_TTL_SECONDS
    return true
end

local function ensureSampleCoins(player: Player): IntValue?
    local leaderstats = player:FindFirstChild("leaderstats")

    if leaderstats == nil then
        local folder = Instance.new("Folder")
        folder.Name = "leaderstats"
        folder.Parent = player
        leaderstats = folder
    end

    if not leaderstats:IsA("Folder") then
        return nil
    end

    local existing = leaderstats:FindFirstChild("SampleCoins")
    if existing ~= nil then
        if existing:IsA("IntValue") then
            return existing
        end
        return nil
    end

    local coins = Instance.new("IntValue")
    coins.Name = "SampleCoins"
    coins.Value = 0
    coins.Parent = leaderstats
    return coins
end

local function getLivingCharacterRoot(player: Player): (BasePart?, Humanoid?)
    local character = player.Character
    if character == nil then
        return nil, nil
    end

    local humanoid = character:FindFirstChildOfClass("Humanoid")
    local root = character:FindFirstChild("HumanoidRootPart")

    if humanoid == nil or humanoid.Health <= 0 then
        return nil, nil
    end
    if root == nil or not root:IsA("BasePart") then
        return nil, nil
    end

    return root, humanoid
end

local function collectSample(player: Player, targetValue: unknown): (boolean, string)
    if typeof(targetValue) ~= "Instance" or not targetValue:IsA("BasePart") then
        return false, "InvalidTarget"
    end

    local target = targetValue :: BasePart
    if not target:IsDescendantOf(workspace) then
        return false, "InvalidTarget"
    end
    if not CollectionService:HasTag(target, COLLECTIBLE_TAG) then
        return false, "NotCollectible"
    end
    if target:GetAttribute("Enabled") == false then
        return false, "Unavailable"
    end

    local root = getLivingCharacterRoot(player)
    if root == nil then
        return false, "NotReady"
    end
    if (root.Position - target.Position).Magnitude > MAX_COLLECTION_DISTANCE then
        return false, "TooFarAway"
    end

    local now = os.clock()
    local lastCollect = lastCollectAt[player.UserId]
    if lastCollect ~= nil and now - lastCollect < COLLECTION_COOLDOWN_SECONDS then
        return false, "Cooldown"
    end

    local collected = collectedByUser[player.UserId]
    if collected == nil then
        collected = {}
        collectedByUser[player.UserId] = collected
    end
    if collected[target] then
        return false, "AlreadyCollected"
    end

    local coins = ensureSampleCoins(player)
    if coins == nil then
        return false, "CurrencyUnavailable"
    end

    -- No yield occurs between the final ownership check and the grant. The
    -- amount is fixed by the server; the client never submits a reward amount.
    coins.Value += REWARD_AMOUNT
    collected[target] = true
    lastCollectAt[player.UserId] = now

    return true, "Collected"
end

local function onRequest(
    player: Player,
    actionId: unknown,
    requestId: unknown,
    target: unknown
)
    if not allowRequest(player) then
        resultEvent:FireClient(player, false, "TooManyRequests", requestId)
        return
    end

    if actionId ~= ACTION_COLLECT_SAMPLE then
        resultEvent:FireClient(player, false, "UnknownAction", requestId)
        return
    end

    if not isValidRequestId(requestId) then
        resultEvent:FireClient(player, false, "InvalidRequestId", nil)
        return
    end

    local validRequestId = requestId :: string
    if not rememberRequestId(player, validRequestId) then
        resultEvent:FireClient(player, false, "DuplicateRequest", validRequestId)
        return
    end

    local success, resultCode = collectSample(player, target)
    resultEvent:FireClient(player, success, resultCode, validRequestId)
end

requestEvent.OnServerEvent:Connect(onRequest)

local function initializePlayer(player: Player)
    ensureSampleCoins(player)
end

Players.PlayerAdded:Connect(initializePlayer)
Players.PlayerRemoving:Connect(function(player: Player)
    requestWindows[player.UserId] = nil
    lastCollectAt[player.UserId] = nil
    processedRequestIds[player.UserId] = nil
    collectedByUser[player.UserId] = nil
end)

for _, player in Players:GetPlayers() do
    task.spawn(initializePlayer, player)
end
