# dgamelaunch installation and configuration notes

These notes consolidate the useful content from `dgamelaunch-setup.pdf` and
`dgamelaunch-setup-2.pdf`.

The main source is Rubén Llorente, “Setting up a dgamelaunch game server: A
Blast from the Past,” *Linux Magazine*, issue 247 (2021). The PDFs were saved in
June 2023. Treat package names, URLs, binary/library paths, service syntax, and
security advice as historical until verified against the target system.

## Architecture

The example uses this connection path:

```text
client -> openbsd-inetd -> telnetd -> dgamelaunch
                                      |
                                      +-> chroot /var/dgl
                                      +-> drop to games:games
                                      +-> launch games
```

dgamelaunch is a restricted launcher that authenticates players, presents game
menus, maintains shared scoreboards, records sessions, lets users watch games in
progress, and can relay spectator messages to games that support its messaging
integration.

It chroots into `/var/dgl`, then drops privileges. A chroot is only one layer of
containment: root inside a chroot may be able to escape it or abuse device nodes
or links. Correct privilege dropping and filesystem permissions remain
essential.

## Network security

The article's Telnet setup is suitable only for a trusted home LAN. Telnet sends
credentials unencrypted and Internet-facing Telnet attracts automated account
creation and brute-force attacks. dgamelaunch and the demonstrated telnetd setup
do not provide adequate abuse controls.

Public Roguelike servers generally expose dgamelaunch through SSH instead. SSH
encrypts the connection, offers better defenses against bots, and does not need
inetd. The article does not document the SSH setup.

## Build dgamelaunch on Debian

Install the build dependencies as root:

```sh
apt-get install automake autoconf build-essential git bison sqlite3 \
  libsqlite3-dev curl unzip groff libncurses-dev flex-old
```

Clone and build with SQLite user storage, shared-memory support, and a
configuration path inside the intended chroot:

```sh
git clone https://github.com/paxed/dgamelaunch.git
cd dgamelaunch
./autogen.sh --enable-sqlite --enable-shmem \
  --with-config-file=/var/dgl/etc/dgamelaunch.conf
make
```

The article says dgamelaunch was not packaged by major distributions and had
not made an official release since 2011, but remained in use and received
community patches. That status should be rechecked before following these build
steps.

## Create the chroot

Edit the source tree's `dgl-create-chroot` script. The article's minimal,
Rogue-oriented example uses:

```sh
CHROOT="/var/dgl/"
USRGRP="games:games"
SQLITE_DBFILE="/dgldir/dgamelaunch.db"

# Empty disables installation of gzip in the chroot.
COMPRESSBIN=""

# Empty because this example is not installing NetHack.
NETHACKBIN=""
NH_PLAYGROUND_FIXED=""

# The NetHack-related variables still required by the script.
NHSUBDIR="/nh343/"
NH_VAR_PLAYGROUND="/nh343/var/"
```

Run it as root:

```sh
bash dgl-create-chroot
```

This should create `/var/dgl` and populate it with the libraries and
configuration files required by the chroot. The script is NetHack-centric, even
when another game is being installed.

The article then installs the launcher setuid-root outside the chroot:

```sh
cp dgamelaunch /usr/bin/
chmod 4755 /usr/bin/dgamelaunch
```

Setuid is what permits the launcher to enter the chroot before shedding
privileges. This is security-sensitive and should be checked against the current
upstream installation instructions. The later inetd example invokes
`/var/dgl/dgamelaunch`, not `/usr/bin/dgamelaunch`; confirm which launcher copy
`dgl-create-chroot` creates and which path the installed telnetd expects.

## Install a game: Rogue V3 example

The article uses John “Elwin” Edwards's preserved early-Roguelike collection and
Rogue V3. Its displayed download URL contains spaces and may require URL
escaping or quoting:

```text
gopher://gopher.operationalsecurity.es/9/Software/Early Roguelikes/ElwinR-rl-74351bf23e5e.zip
```

The original sequence, with an apparent missing space in the printed
`configure` command corrected, is:

```sh
curl -LO 'gopher://gopher.operationalsecurity.es/9/Software/Early Roguelikes/ElwinR-rl-74351bf23e5e.zip'
unzip ElwinR-rl-74351bf23e5e.zip
cd ElwinR-rl-74351bf23e5e/rogue3
autoreconf
./configure \
  --enable-savedir=/var/games/rogue3/save \
  --enable-scorefile=/var/games/rogue3/rogue.scr \
  --enable-logfile=/var/games/rogue3/rogue.log
make
```

Those paths are system-wide game paths as seen *inside* the chroot. Create the
corresponding directories and install the binary:

```sh
cd /var/dgl
mkdir -p var/games/rogue3/save
mkdir -p usr/games
mkdir -p dgldir/inprogress-rogue3
cp "$HOME/ElwinR-rl-74351bf23e5e/rogue3/rogue3" usr/games/
chown -R games:games var/games dgldir
```

Every dynamically linked game needs its runtime libraries copied into the
chroot. The article's Rogue example copies ncurses on x86-64 Debian:

```sh
cp /lib/x86_64-linux-gnu/libncurses.so.6 \
  /var/dgl/lib/x86_64-linux-gnu/
```

Do not assume that one library is sufficient on a current system; inspect the
game binary's dependencies and reproduce the required loader and library paths
inside the chroot.

Other terminal games can be integrated in the same manner. The article mentions
Debian's `bsdgames` package, including `phantasia`, `battlestar`, and `trek`.

## Example `dgamelaunch.conf`

The configured location is `/var/dgl/etc/dgamelaunch.conf`:

```conf
chroot_path = "/var/dgl"
dglroot = "/dgldir/"
banner = "/dgl-banner"
shed_uid = 5
shed_gid = 60

commands[register] = mkdir "%ruserdata/%n",
 mkdir "%ruserdata/%n/ttyrec",
 mkdir "%ruserdata/%n/ttyrec/rogue3"

commands[login] = mkdir "%ruserdata/%n",
 mkdir "%ruserdata/%n/ttyrec",
 mkdir "%ruserdata/%n/ttyrec/rogue3"

menu["mainmenu_anon"] {
 bannerfile = "/dgl_menu_main_anon.txt"
 commands["l"] = ask_login
 commands["r"] = ask_register
 commands["w"] = watch_menu
 commands["q"] = quit
}

menu["mainmenu_user"] {
 bannerfile = "/dgl_menu_main_user.txt"
 commands["c"] = chpasswd
 commands["e"] = chmail
 commands["w"] = watch_menu
 commands["3"] = play_game "RogueV3"
 commands["q"] = quit
}

menu["watchmenu_help"] {
 bannerfile = "/dgl_menu_watchmenu_help.txt"
 commands["qQ "] = return
}

DEFINE {
 game_path = "/usr/games/rogue3"
 game_name = "Rogue V3 (3.6)"
 short_name = "RogueV3"
 game_args = "rogue3", "-n", "%n"
 inprogressdir = "%rinprogress-rogue3/"
 ttyrecdir = "%ruserdata/%n/ttyrec/rogue3/"
 commands = cp "/var/games/rogue3/save/%u-%n.r3sav" "/var/games/rogue3/save/%u-%n.r3sav.bak"
}
```

Key points from the article:

- `shed_uid` and `shed_gid` are the numeric identity dgamelaunch assumes after
  entering the chroot. Values `5:60` corresponded to `games:games` on the
  author's Debian system; resolve the IDs on the actual host rather than copying
  them blindly.
- `commands[register]` creates the per-user recording directories.
- `commands[login]` repairs those directories if they are missing later.
- `game_path` is the game's absolute path as seen inside the chroot.
- `game_args` supplies its argument vector and player name.
- `inprogressdir` enables in-progress game tracking/viewing.
- `ttyrecdir` stores recorded sessions.
- The game-level `commands` entry copies the player's save to a backup whenever
  the game starts.
- The source distribution contains more annotated configuration examples.

## User menu

The default user menu was NetHack-specific. The Rogue replacement shown for
`/var/dgl/dgl_menu_main_user.txt` is:

```text
##
## $VERSION - network console game launcher
## Copyright (c) 2000-2009 The Dgamelaunch Team
## See http://nethack.wikia.com/wiki/dgamelaunch for more info
##
## Games on this server are recorded for in-progress viewing and playback!

Logged in as: $USERNAME

c) Change password             e) Change email address
w) Watch games in progress
3) Play Rogue V3
q) Quit
=>
```

The keys displayed here must agree with the commands in `mainmenu_user`.

## Test locally

Run the installed launcher as an ordinary user:

```sh
/usr/bin/dgamelaunch
```

A successful launch enters `/var/dgl` and presents the anonymous menu, from
which a test user can register, log in, play, and watch active games.

## Historical Telnet/inetd setup

Again, this is for a trusted LAN, not the public Internet. Install the services:

```sh
apt-get install openbsd-inetd telnetd
```

The article says to make this the only line in `/etc/inetd.conf`:

```text
telnet stream tcp nowait root.root /usr/sbin/tcpd /usr/sbin/in.telnetd -h -L /var/dgl/dgamelaunch
```

This has inetd accept Telnet connections, run telnetd through `tcpd`, and make
dgamelaunch the session shell. Reload inetd afterward:

```sh
systemctl reload inetd
```

Current Debian package contents, daemon flags, tcp-wrappers availability, and
service unit name may differ.

## Recordings, watching, and messages

With the example configuration, recordings are stored below:

```text
/var/dgl/dgldir/userdata/$USER/ttyrec/rogue3/
```

They can be played with a ttyrec player such as `ttyplay`, and public servers
commonly make recordings downloadable over HTTP. Connected users can watch
active games.

Games patched for dgamelaunch integration, including NetHack and Dungeon Crawl
Stone Soup, can receive spectator messages. The article warns that attempting
message delivery for a game without a configured `spooldir` crashes the relevant
dgamelaunch process, although it does not terminate players' game processes.
Disable/avoid messaging until that integration is configured.

## References preserved from the PDFs

The one-page note contained only this reference list; it had no findings about
how individual server operators customized dgamelaunch:

- Upstream repository and README: <https://github.com/paxed/dgamelaunch> and
  <https://github.com/paxed/dgamelaunch#readme>
- Paxed's setup notes:
  <https://nethackwiki.com/wiki/User:Paxed/HowTo_setup_dgamelaunch>
- NetHackWiki dgamelaunch overview:
  <https://nethackwiki.com/wiki/Dgamelaunch>
- Linux Magazine article:
  <https://www.linux-magazine.com/Issues/2021/247/dgamelaunch>

Additional links cited by the article:

- Rogue V3 history: <https://rlgallery.org/about/rogue3.html>
- Dungeon Crawl Stone Soup: <https://crawl.develz.org/>
- NetHack.alt.org: <https://alt.org/nethack/>
- Roguelike Gallery: <https://rlgallery.org>
- Roguelike Gallery's dgamelaunch SSH service (the article gives username
  `rodney` and password `yendor`): <https://rlgallery.org:8080>
- DCSS online-server list (historical HTTP URL):
  <http://crawl.chaosforge.org/Playing_online>

## What the PDFs do not establish

The notes do not contain the intended survey of modifications made by notable
NetHack server operators. They name Paxed, NetHack.alt.org, Roguelike Gallery,
and Dungeon Crawl Stone Soup as starting points, but provide no patches,
configuration deltas, repository forks, or operator-specific design findings.
That investigation remains separate work.
