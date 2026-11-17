# Install & Annual Maintenance

How to wire and hang the 13 lanterns in the front-yard Deodar cedar, and how to look after them once a year. The parts are in [bom.md](bom.md). The reasoning behind them is in the [power & wiring design](superpowers/specs/2026-11-16-power-wiring-design.md).

**Three rules hold throughout:**
- Nothing is screwed, nailed or stapled into the tree.
- Nothing is tied around the trunk.
- The cable never carries a lantern's weight.

## 1. Before you start

- [ ] Cube readings are recorded in [TODO.md](../TODO.md). The cabling below can go in before them; the lanterns' boards can't.
- [ ] The tree survey is done: 13 spots grouped by limb into 2–3 trunk runs, with cable lengths measured.
- [ ] Each lantern is assembled: panels in, roof screwed down, and the cord out through the eye with an SP13 **male** on a ~30 cm pigtail.
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

1. At the splice point, attach one drop cable per lantern to the trunk with a **gel-filled splice connector**.
2. Run each drop along the limb toward its lantern spot, tied loosely about every 40 cm.
3. Fit an SP13 **female** on the end of each drop, and let it hang a little below the limb.

## 5. Hanging a lantern

The ladder steps below need both hands. Have a helper foot the ladder, and keep three points of contact while you climb.

1. Girth-hitch a webbing sling **loosely** over the limb, padding the bark. Don't cinch it tight.
2. Clip a 316 quick link to the sling, and hang the chain from it.
3. Hook the lantern's roof eye onto the chain. Check that it hangs plumb and clears nearby branches when they move in the wind.
4. Plug the lantern's SP13 male into the drop's female and screw the collar down until the seal seats.
5. Form a **drip loop** below the connector, so the cable dips lower than the eye.
6. Add a strain-relief tie that holds the cord to the chain near the eye. A tug on the cord should pull the chain, not the cord's joints inside the lantern.

## 6. Power-on check

1. Turn the cedar's group on at 100% in the Luxor app. All 13 lanterns should light and flicker independently.
2. Step it down to 50%, then 10%. Every lantern should follow the dimming.
3. If one lantern is dark, check its SP13 connection first, then its splice.

## 7. Annual maintenance (once a year, before summer)

- [ ] **Trunk loops:** loosen any loop that's getting tight against bark, and re-tie it with slack.
- [ ] **Limb ties:** same check. Replace any brittle or sun-cracked ties.
- [ ] **Slings:** look for UV fading, fraying or stiffness, and replace any that show it. Webbing in full sun lasts a few seasons.
- [ ] **Chain and quick links:** check the gates are closed and there's no wear at the roof eye.
- [ ] **SP13 connectors:** unscrew one or two to check the seals are seated and there's no water inside. Re-seat the collars.
- [ ] **Drip loops:** make sure they're still lower than each connector and gland.
- [ ] **Roof screw wells:** check the sealant or plugs are intact.
- [ ] **Panels and frame:** look for cracks, sagging, or creep at the eye from heat, and replace any affected part.
- [ ] **Base enclosure:** check it's dry inside, the glands are tight, and the drain is clear.
