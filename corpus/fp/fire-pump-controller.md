# Fire-pump controller and supervision

Company scope is a pump serving wet, dry, or double-interlock sprinklers. Electric (with or without a transfer switch) and diesel are both in scope. Series pumps are not. On FM work, disable series, higher-zone, and lower-zone functions and say so on the submittal. FM DS 3-7 is the sheet; confirm the revision in hand (`[V]` if the pack's 2021 reading is all you have).

## Configuration refuse list

Do not enable lockout, load shed, or automatic stop. Those functions defeat a fire pump. State on the submittal that they are off.

Starter: use reduced-voltage starting where the motor is 100 hp or larger, or where the pump is on a generator. Flag the choice. Across-the-line is not the default in those two cases.

## Signals

Map each required remote signal to a named terminal. NFPA 20 §10.4.7 (electric), §12.4.2 (diesel), and §4.18 are the controller-side cites. The fire-alarm class and the module count are `fa-fire-pump-and-preaction-supervisory-points` (NFPA 72 §23.8.5.9 and §17.19).

Diesel trouble grouping, as a design-practice reading of the common option under NFPA 20 §12.4.2.3(3): one common diesel trouble point, unless the owner, FM, or the authority having jurisdiction asks for the discrete points. FM also accepts a single pump-house trouble signal on the DS 3-7 reading in the pack. Confirm the current revision.

## Room

Publish both the minimum and the maximum pump-room temperature the controller listing allows. A transfer-switch outage budget belongs in the cause-and-effect narrative when a transfer switch is present. Do not invent a cooling-continuation time after power isolation. Order the outputs and mark the hold time `[V]`.
