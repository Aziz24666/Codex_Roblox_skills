# Moderation workflow, privacy, and appeals

V32 provides a human-reviewed workflow checklist and an offline schema for moderation case metadata. It is not a moderation service, a Roblox reporting replacement, or an automated sanction engine.

## Keep platform reporting available

Preserve Roblox's built-in Report Abuse flow and authorized Creator Dashboard safety tools. Do not force a player to submit a custom in-game form instead of the platform report flow.

- [Roblox safety and creator tools](https://create.roblox.com/docs/safety)
- [Players and experience bans](https://create.roblox.com/docs/reference/engine/classes/Players)
- [Experience guidelines and moderation](https://create.roblox.com/docs/production/promotion/experience-guidelines)

## Publish clear and consistently applied rules

Make experience rules accessible. Define categories, severity, review priorities, evidence handling, and an appeal route. Apply rules consistently rather than arbitrarily targeting users. Record a concise policy outcome, not an accusation or narrative about a person.

Roblox's player guidance states that users may appeal to creators when they believe a creator-issued experience ban was incorrect. Provide a real review path. Use supported ban controls only through authorized, human-operated workflows and follow current API usage guidance.

## Keep case files privacy-minimal

The V32 case format accepts only:
- An opaque internal case reference.
- A source, category, channel, severity, and workflow state selected from fixed codes.
- Opaque evidence references, not file paths, links, usernames, or content.
- Reviewer roles, timestamps, a fixed decision code, and a limited appeal state.

Do not add reporter/target user IDs, usernames, raw chat, voice recordings, personal details, screenshots, free-text allegations, or copied player records to the case JSON or Codex project. Keep necessary identity and original evidence within authorized Roblox moderation systems and access-controlled storage.

## Human review and second review

- Treat a report as a request to investigate, not proof that a rule was broken.
- Review relevant platform evidence with authorized access.
- Record the rule and evidence category used in the decision.
- Require a second authorized reviewer for high-impact severities when the policy says so.
- Do not sanction anyone solely because a report-count threshold, heuristic, static code scan, or unverified signal fired.
- Preserve a way to correct mistakes, receive appeals, and record whether an appeal was upheld, modified, or overturned.

V32 automated_enforcement must be false. The tool validates records; it never bans, kicks, mutes, removes content, or changes live settings.

## Validate policy and records

Copy the examples from v32/examples/ into the selected project under .codex/moderation/. Adapt review times and retention values to your team's resourcing and applicable requirements; the sample values are not legal advice or Roblox-mandated SLAs.

    python .\v32\tools\v32.py validate-policy --root C:\Path\To\YourGame
    python .\v32\tools\v32.py validate-case --root C:\Path\To\YourGame
    python .\v32\tools\v32.py validate-register --root C:\Path\To\YourGame

Set a documented retention schedule, minimize copied evidence, restrict reviewer access, and securely delete records when the retention purpose ends.
