-- Nexus minimal starting level.
-- NetHack may be freely redistributed. See license for details.

des.level_init({ style = "solidfill", fg = " " });
des.level_flags("mazelevel", "noflip", "premapped", "nomongen",
                "nodeathdrops", "solidify");

des.map([[
-------------------------
|.......................|
|.......................|
|.......................|
|.......................|
|.......................|
-------------------------
]]);

des.region(selection.area(00,00,24,06), "lit");
des.non_diggable(selection.area(00,00,24,06));
des.non_passwall(selection.area(00,00,24,06));

des.stair("up", 12, 3);
des.stair("down", 12, 5);
des.object({ id = "apple", coord = { 10, 3 } });
des.object({ id = "lamp", coord = { 14, 3 } });
des.monster({ id = "newt", coord = { 18, 3 }, peaceful = true });
