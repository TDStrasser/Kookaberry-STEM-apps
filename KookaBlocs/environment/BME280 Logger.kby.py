import machine, kooka
import time
import fonts
from bme280 import BME280
from machine import SoftI2C

log_headings = None
data_to_log = None
i = None

weekday_names = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
def datetime_format(*args, rtc=machine.RTC()):
    dt = rtc.datetime()
    s = ""
    for f in args:
        if f == "weekday":
            f = weekday_names[dt[3] - 1]
        else:
            f = f.format(*dt)
        s += f
    return s

def upRange(start, stop, step):
    while start <= stop:
        yield start
        start += abs(step)

def downRange(start, stop, step):
    while start >= stop:
        yield start
        start -= abs(step)

# Define global objects.
i2c_P3BP3A = SoftI2C(scl="P3B", sda="P3A")
bme280_i2c_P3BP3A_0x77 = BME280(address=0x77, i2c=i2c_P3BP3A)



# Initialise timer counters.
_timer30000 = time.ticks_ms()

# On-start code, run once at start-up.
if True:
    log_headings = ['Temp C', 'Rel Humid %', 'Press HPa']
    with open("data.csv", "w+") as f: pass
    with open("data.csv", "at") as f:
        f.write("{},{}\n".format('Date,Time', ','.join(log_headings)))

# Main loop code, run continuously.
while True:
    if time.ticks_diff(time.ticks_ms(), _timer30000) >= 0:
        _timer30000 += 30000
        kooka.display.fill(0)
        kooka.display.setfont(fonts.mono8x8)
        kooka.display.print('BME280 Logger', show=0)
        data_to_log = ["{:5.1f}".format(bme280_i2c_P3BP3A_0x77.values[0]), "{:5.1f}".format(bme280_i2c_P3BP3A_0x77.values[2]), "{:5.1f}".format(bme280_i2c_P3BP3A_0x77.values[1])]
        with open("data.csv", "at") as f:
            f.write("{},{}\n".format(datetime_format("{0}/{1:02}/{2:02}", ",", "{4:02}:{5:02}:{6:02}"), ','.join(data_to_log)))
        kooka.display.setfont(fonts.mono6x7)
        i_end = float(len(log_headings) - 1)
        for i in (0 <= i_end) and upRange(0, i_end, 1) or downRange(0, i_end, 1):
            kooka.display.print(log_headings[int(i)], data_to_log[int(i)], show=0)
        kooka.display.print('Last Sample:', show=0)
        kooka.display.print(datetime_format("{2:02}/{1:02}/{0}", "-", "{4:02}:{5:02}:{6:02}"), show=0)
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="w@~/7{qk$Ex$kK,P!~b8">log_headings</variable><variable id="gBFoEOJ-Ua$u_AGWJq#u">data_to_log</variable><variable id="[d8iGuKRQp:K9|wSg5`N">i</variable></variables><block type="event_on_start" id="y`9REB6+-63(gbI1)9NU" x="130" y="-430"><statement name="DO"><block type="variables_set" id="*CfQqxTT(NkcwzzF)pil"><field name="VAR" id="w@~/7{qk$Ex$kK,P!~b8">log_headings</field><value name="VALUE"><block type="lists_create_with" id="tQXq*lHv^8[?3xZre{:/"><mutation items="3"></mutation><value name="ADD0"><block type="text" id="}z7[WEp.153W2Dg_0@K;"><field name="TEXT">Temp C</field></block></value><value name="ADD1"><block type="text" id="o}u=8RHvt6c7EQY)EPq]"><field name="TEXT">Rel Humid %</field></block></value><value name="ADD2"><block type="text" id="y3YX9kU=LK3:3LSXa;U}"><field name="TEXT">Press HPa</field></block></value></block></value><next><block type="py_stmt" id="kAWa#~Sf[1Xx!K8C9.|%"><field name="STMT">with open("data.csv", "w+") as f: pass</field><next><block type="file_log_data" id="DCV?M(Bb3aaf^afc5p`!"><field name="FILE">data.csv</field><value name="VALUE1"><block type="text" id="rG4ay4H]7`]Gg1P{|0q%"><field name="TEXT">Date,Time</field></block></value><value name="VALUE2"><shadow type="math_number" id="dQDtIKOnr[n*5o0o]$T1"><field name="NUM">1.2</field></shadow><block type="lists_split" id="R+Ios2q1Dp|)}DjL{(^P"><mutation mode="JOIN"></mutation><field name="MODE">JOIN</field><value name="INPUT"><block type="variables_get" id="F*~^aI@^$1TmQsgL+Y/e"><field name="VAR" id="w@~/7{qk$Ex$kK,P!~b8">log_headings</field></block></value><value name="DELIM"><shadow type="text" id="l?MT4:@.;|*4tB@eLmQ#"><field name="TEXT">,</field></shadow></value></block></value></block></next></block></next></block></statement></block><block type="event_every_seconds" id="0_!.b}aAr9f98/P(+cOB" x="130" y="-190"><field name="T">30</field><statement name="DO"><block type="display_clear" id=";`8ufAwn8K@u:F=P;J#,"><next><block type="display_setfont" id="Cd=]#IE|t|78VuSy2~rb"><field name="FONT">mono8x8</field><next><block type="display_print" id="1Qn]7uWhzbZMf1!$v~BJ"><value name="VALUE"><shadow type="text" id="9CoOsu#OCe0X:0Er]^OT"><field name="TEXT">BME280 Logger</field></shadow></value><next><block type="variables_set" id="s6iS,=VC}vK|S+{~`u?6"><field name="VAR" id="gBFoEOJ-Ua$u_AGWJq#u">data_to_log</field><value name="VALUE"><block type="lists_create_with" id="C:;grGUy6tUklF?4+fGz"><mutation items="3"></mutation><value name="ADD0"><block type="str_format_float" id="s$sMce`;=^3M}GNWbG1E"><field name="D">1</field><field name="W">5</field><value name="VALUE"><block type="bme280_read_param" id="$g{!@pIymkF!7FFcv`B/"><field name="PARAM">.values[0]</field><field name="ADDRESS">0x77</field><field name="SCL">P3B</field><field name="SDA">P3A</field></block></value></block></value><value name="ADD1"><block type="str_format_float" id="BhG;zLvr[;+O]Vye)gI2"><field name="D">1</field><field name="W">5</field><value name="VALUE"><block type="bme280_read_param" id="C[*_(Z8m`+619Nyuc[a{"><field name="PARAM">.values[2]</field><field name="ADDRESS">0x77</field><field name="SCL">P3B</field><field name="SDA">P3A</field></block></value></block></value><value name="ADD2"><block type="str_format_float" id=":7p![-skeKE`Put.^Sf8"><field name="D">1</field><field name="W">5</field><value name="VALUE"><block type="bme280_read_param" id="cH88Iz-2Nr=S_^!_j``{"><field name="PARAM">.values[1]</field><field name="ADDRESS">0x77</field><field name="SCL">P3B</field><field name="SDA">P3A</field></block></value></block></value></block></value><next><block type="file_log_data" id="Xm3,w:kHny[UeDPC!R1!"><field name="FILE">data.csv</field><value name="VALUE1"><block type="rtc_datetime2" id="$jXCi*uVJR4U7t4kQ)Ze"><field name="DATETIME1">{0}/{1:02}/{2:02}</field><field name="SEP">,</field><field name="DATETIME2">{4:02}:{5:02}:{6:02}</field></block></value><value name="VALUE2"><shadow type="math_number" id="rc~D}A@o3Dh5._p:F0e%"><field name="NUM">1.2</field></shadow><block type="lists_split" id=";11I^RFB:lBc)ALXJVgB"><mutation mode="JOIN"></mutation><field name="MODE">JOIN</field><value name="INPUT"><block type="variables_get" id="Ons#QuME9lZ;$HlN:MTL"><field name="VAR" id="gBFoEOJ-Ua$u_AGWJq#u">data_to_log</field></block></value><value name="DELIM"><shadow type="text" id="LZOZglOPg(W-vV;!c4Ot"><field name="TEXT">,</field></shadow></value></block></value><next><block type="display_setfont" id="MEepBMi}i#1eET!*Ny!$"><field name="FONT">mono6x7</field><next><block type="controls_for" id="3X/k^o2$yhr}N;I;Y5f`"><field name="VAR" id="[d8iGuKRQp:K9|wSg5`N">i</field><value name="FROM"><block type="math_number" id="*(nH)K%y-}:JWPz@Ry-Q"><field name="NUM">0</field></block></value><value name="TO"><block type="math_arithmetic" id="%T*=#m#GtR5/Tdy?.S`y"><field name="OP">MINUS</field><value name="A"><shadow type="math_number" id="M6[NwD*7{2ASBXSlLF95"><field name="NUM">1</field></shadow><block type="lists_length" id="Hf(3~)ODSxo?pS9~[Sx."><value name="VALUE"><block type="variables_get" id="z~Awbavy_0IOsc?3Q$(3"><field name="VAR" id="w@~/7{qk$Ex$kK,P!~b8">log_headings</field></block></value></block></value><value name="B"><shadow type="math_number" id="/onU+^uGP=CZ+Uhh=h*g"><field name="NUM">1</field></shadow></value></block></value><value name="BY"><block type="math_number" id="ZvploAv_s]Byd*f;l(ux"><field name="NUM">1</field></block></value><statement name="DO"><block type="display_print2" id="FPIEL|ua-h~tQnmZM|dq"><value name="VALUE1"><shadow type="text" id="r}7rtPZcdlDDbH8GEJop"><field name="TEXT">Hello</field></shadow><block type="lists_getIndex" id="C`z%;CW}}]*v!ut)!,dC"><mutation statement="false" at="true"></mutation><field name="MODE">GET</field><field name="WHERE">FROM_START</field><value name="VALUE"><block type="variables_get" id="x-vKw{rlHf0MMYaCMA`V"><field name="VAR" id="w@~/7{qk$Ex$kK,P!~b8">log_headings</field></block></value><value name="AT"><block type="variables_get" id="I%Y|*cc38D[EyJ#AMRIv"><field name="VAR" id="[d8iGuKRQp:K9|wSg5`N">i</field></block></value></block></value><value name="VALUE2"><shadow type="math_number" id="v*io_PmOs7Fh,~_O[dvg"><field name="NUM">123</field></shadow><block type="lists_getIndex" id="vOG(A.SpSYRV[@^z;54W"><mutation statement="false" at="true"></mutation><field name="MODE">GET</field><field name="WHERE">FROM_START</field><value name="VALUE"><block type="variables_get" id="g8pF=#i;OQ#-AI,.gwA;"><field name="VAR" id="gBFoEOJ-Ua$u_AGWJq#u">data_to_log</field></block></value><value name="AT"><block type="variables_get" id="hu_[5Bmh+rl[w1Aqg/2,"><field name="VAR" id="[d8iGuKRQp:K9|wSg5`N">i</field></block></value></block></value></block></statement><next><block type="display_print" id="uSN}hvD4NXTk4y.G|*B_"><value name="VALUE"><shadow type="text" id="mRjOdI3$c~n|le;O`]x`"><field name="TEXT">Last Sample:</field></shadow></value><next><block type="display_print" id="G^VMo%6{K+i!n$wHl0`b"><value name="VALUE"><shadow type="text" id="5~!l8ea.KON+n$S#@/0u"><field name="TEXT">Hello</field></shadow><block type="rtc_datetime2" id="7q4^ZfK$)5GHKu.@@qmf"><field name="DATETIME1">{2:02}/{1:02}/{0}</field><field name="SEP">-</field><field name="DATETIME2">{4:02}:{5:02}:{6:02}</field></block></value></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block></xml>
