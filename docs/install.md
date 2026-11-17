# Install & Annual Maintenance

How to wire and hang the 13 lanterns in the front-yard Deodar cedar, and how to look after them once a year. The parts are in [bom.md](bom.md). The reasoning behind them is in the [power & wiring design](superpowers/specs/2026-11-16-power-wiring-design.md).

**Three rules hold throughout:**
- Nothing is screwed, nailed or stapled into the tree.
- Nothing is tied around the trunk.
- The cable never carries a lantern's weight.

## 1. Before you start

- [ ] Cube readings are recorded in [TODO.md](../TODO.md). The cabling below can go in before them; the lanterns' boards can't.
- [ ] The tree survey is done: 13 spots grouped by limb into 2–3 trunk runs, with cable lengths measured.
- [ ] Each lantern is assembled: panels in, roof screwed down, and the cord out through the post-corner opening with an SP13 **male** on a ~30 cm pigtail.
- [ ] **The cedar's Luxor group is turned off** in the Luxor app, or the transformer is switched off, before you touch any wire.

## 2. Base junction

1. Run each trunk cable into the existing enclosure through its own IP68 cable gland. Leave a **drip loop** below each gland, so water runs off the bottom of the loop instead of into the box.
2. Connect every trunk to the Cube's output with Wago 221 lever connectors, matching the conductors consistently. Polarity doesn't matter, because the boards are non-polarized, but consistency helps when tracing faults.
3. Keep the enclosure's drain path clear. Mount it so the cable entries face down.

## 3. Trunk runs

1. Take each trunk cable up the **shaded side** of the trunk, lying in the bark furrows.
2. Hold it **only at limb crotches**, with a padded, loose loop of rubber-coated tie around the limb, not the trunk.
3. Leave about a finger's width of slack in every loop, so the tree can grow.
4. Stop at the trunk's limb splice point, chosen during the survey.

## 4. Limb splices and drops

1. At the splice point, join each drop cable to the trunk with **two gel-filled splice connectors**, one per conductor.
2. Run each drop along the limb toward its lantern spot, tied loosely about every 40 cm.
3. Let the drop come down beside where the chain will hang, long enough to reach the lantern. Fit an SP13 **female** on its end. The connector belongs **at the lantern**, not up at the limb.
4. Make a drip loop in the drop just above the connector, so water running down the drop drips off before it reaches the connector.

## 5. Hanging a lantern

The ladder steps below need both hands. Have a helper foot the ladder, and keep three points of contact while you climb.

1. Drape the webbing sling over the limb in a **basket hitch**: over the top, with both ends brought down to the quick link. The webbing pads the bark and spreads the load. A basket hitch can't cinch, but a girth or choker hitch would tighten under the lantern's weight and girdle the limb over the years.
2. Clip both sling ends into a 316 quick link, and hang the chain from it.
3. Hook the lantern's eye bolt onto the chain. Check that it hangs plumb and clears nearby branches when they move in the wind.
4. Plug the lantern's SP13 male into the drop's female next to the lantern, and screw the collar down until the seal seats.
5. The pigtail leaves the lantern through the post corner just below the top rail. Let it dip into a **drip loop below that opening** before it rises to the connector.
6. Tie the drop loosely to the chain every 20–30 cm with **some slack**, and add a strain-relief tie that holds the pigtail to the chain near the eye. The chain carries the lantern; the cable must never go taut. A tug on the cord should pull the chain, not the cord's joints inside the lantern.

## 6. Power-on check

1. Turn the cedar's group on at 100% in the Luxor app. All 13 lanterns should light and flicker independently.
2. Step it down to 50%, then 10%. Every lantern should follow the dimming.
3. If one lantern is dark, check its SP13 connection first, then its splice.

## 7. Annual maintenance (once a year, before summer)

**Turn the cedar's Luxor group off first.** Never open a wet connector or the enclosure while it's live.

- [ ] **Crotch loops:** these are the limb loops holding the trunk cables at each crotch. Loosen any that's getting tight against bark, and re-tie it with slack.
- [ ] **Limb ties:** same check. Replace any brittle or sun-cracked ties.
- [ ] **Slings:** look for UV fading, fraying or stiffness, and replace any that show it. Webbing in full sun lasts a few seasons. Confirm each one is still a basket hitch and hasn't been re-rigged as a girth hitch.
- [ ] **Chain, quick links and eye bolt:** check the gates are closed, there's no wear at the eye, and the eye bolt doesn't turn or rock. Its top nut and sealing washer should be snug.
- [ ] **SP13 connectors:** unscrew one or two to check the seals are seated and there's no water inside. Re-seat the collars.
- [ ] **Drip loops:** make sure they're still lower than each connector and gland.
- [ ] **Roof screw wells:** check the sealant or plugs are intact.
- [ ] **Panels and frame:** look for cracks or sagging, especially around the roof peak and the two roof screws, and replace any affected part.
- [ ] **Base enclosure:** check it's dry inside, the glands are tight, and the drain is clear.
- [ ] **Power back on:** finish with the 100% → 10% check from section 6.
