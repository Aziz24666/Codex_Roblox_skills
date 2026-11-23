# Player safety by design

The most reliable moderation system reduces opportunities for misuse before reports arrive. Roblox recommends proactive UGC safeguards such as pre-moderation, limited distribution, ephemeral content, trusted-user privileges, and predefined customization choices.

- [Roblox safety design guidance](https://create.roblox.com/docs/safety)
- [Content ratings questionnaire](https://create.roblox.com/docs/production/promotion/content-ratings)
- [Player and creator expectations](https://create.roblox.com/docs/players)

## Review each shared-content feature

For signs, decals, builds, outfits, emotes, profile text, custom names, and shared creations:
1. Identify who can create, edit, view, and share the content.
2. Decide whether the feature can start with predefined choices or a private draft.
3. Consider pre-moderation before publication and limited visibility until review.
4. Use short-lived or reversible sharing where permanence is unnecessary.
5. Provide report and block pathways consistent with Roblox platform features.
6. Apply server-side permission, ownership, rate, size, and placement validation.
7. Review aggregate safety signals after release; do not turn signals into automatic punishments.

## Design for a broad and age-diverse audience

Keep social features understandable and optional. Avoid coercive interactions, public exposure of private details, unsafe environments, and mechanics that pressure players to disclose personal information. Complete and update the Roblox content ratings questionnaire truthfully when the experience changes.

Do not ask players to share real names, contact details, passwords, location, off-platform handles, or other personal information. Avoid collecting raw chat or voice content for custom analytics. Keep reports and moderation decisions private; never create public accusation boards, player-shaming lists, or retaliatory systems.

## Release checklist

- [ ] Platform reporting and blocking remain accessible.
- [ ] All custom text visible to others follows the correct server-side filter flow.
- [ ] Filter failures fail closed; no raw fallback reaches other players.
- [ ] Shared UGC has a clear publication, review, and removal path.
- [ ] Rules, enforcement reasons, and appeals are easy to find.
- [ ] Moderation access is restricted to authorized people.
- [ ] Data retention is documented and limited.
- [ ] High-impact decisions receive the required independent review.
- [ ] Safety checks are re-run after adding a new UGC surface or social feature.

V32 checklists do not replace Roblox Community Standards, Creator Hub requirements, legal obligations, or authorized human review.
