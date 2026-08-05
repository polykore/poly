def run(term, args):

    term.write("""

poly commands


general
-------
help
clear
exit
history
time

filesystem
----------
pwd
cd
ls
mkdir
touch
cat
cp
mv
rm

variables
---------
set
get

shell
-----
cmd
bash
shell
newRun

examples
--------
ls
cd Documents
mkdir Test
touch hello.txt
cat hello.txt
newRun notepad.exe -comp xpsp3 -winamt 3 -time 15
""")