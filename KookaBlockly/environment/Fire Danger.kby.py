import machine, kooka
import time
import fonts
from machine import Pin

temperature = None
danger = None

def onewire_ds18_read_temp(p):
    import onewire, ds18x20
    ds = ds18x20.DS18X20(onewire.OneWire(Pin(p, Pin.PULL_UP)))
    roms = ds.scan()
    if not roms: return -100
    ds.convert_temp()
    time.sleep(0.75)
    return ds.read_temp(roms[0])



# Initialise timer counters.
_timer2000 = time.ticks_ms()

# On-start code, run once at start-up.
if True:
    temperature = onewire_ds18_read_temp("P2")

# Main loop code, run continuously.
while True:
    kooka.display.clear()
    kooka.display.setfont(fonts.mono8x8)
    kooka.display.text(str('Fire Danger'), int(0), int(10), int(1))
    kooka.display.setfont(fonts.sans12)
    kooka.display.text(str("{:4.1f}".format(temperature)), int(0), int(34), int(1))
    kooka.display.text(str('C'), int(50), int(34), int(1))
    kooka.display.setfont(fonts.mono8x8)
    kooka.display.text(str(danger), int(0), int(44), int(1))
    kooka.display.text(str('A - exit'), int(0), int(63), int(1))
    kooka.display.show()
    if time.ticks_diff(time.ticks_ms(), _timer2000) >= 0:
        _timer2000 += 2000
        temperature = onewire_ds18_read_temp("P2")
        if temperature < 25:
            kooka.Servo("P1").angle(60)
            danger = 'Moderate'
        elif temperature < 30:
            kooka.Servo("P1").angle(25)
            danger = 'High'
        elif temperature < 35:
            kooka.Servo("P1").angle(-25)
            danger = 'Extreme'
        else:
            kooka.Servo("P1").angle(-60)
            danger = 'Catastrophic'
    if kooka.button_a.was_pressed():
        raise SystemExit
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="ABC9sGviU5x;BeYi~ZvF">temperature</variable><variable id="s~%TQ81?L-3aRx!u?kbx">danger</variable></variables><block type="event_on_start" id="Kmd;l=}j7fTA_}^]yhV)" x="390" y="-210"><statement name="DO"><block type="variables_set" id="NZ29SKM`n/1Oj2@8OxO*"><field name="VAR" id="ABC9sGviU5x;BeYi~ZvF">temperature</field><value name="VALUE"><block type="onewire_ds18_read_temp_v2" id="mjKmYmXvk]AhK9J4|xIy"><value name="PIN"><block type="pin_selector_sensor" id="Z1G^TwrcLTxGGM2f6ihy"><field name="PIN">"P2"</field></block></value></block></value></block></statement></block><block type="event_every_loop" id="xX`6[$Vr/~ckyk?S%X2," x="950" y="-230"><statement name="DO"><block type="display_clear" id="CL4qi8}ext]f1{)1[9}a"><next><block type="display_setfont" id="kgYW$QoN^*d`r]8sfW);"><field name="FONT">mono8x8</field><next><block type="display_text" id="bUvn=E9J)bZTO4.yk_F."><value name="VALUE"><shadow type="text" id="B-j{{xSLHgq8cCRYzFEH"><field name="TEXT">Fire Danger</field></shadow></value><value name="X"><shadow type="math_number" id="_BLoiCf^,aL(|e!NzB)q"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="*d/@AI,%VG`341!s$AE="><field name="NUM">10</field></shadow></value><value name="C"><shadow type="math_number" id="6o~fNf^79;_V,vF3#*9D"><field name="NUM">1</field></shadow></value><next><block type="display_setfont" id="7mG3u-X;r0H89[y8sO@o"><field name="FONT">sans12</field><next><block type="display_text" id="jShJFsZtrwTZ_?ZvUrwY"><value name="VALUE"><shadow type="text" id="Yb.#?@w.wZo5d7J;70i5"><field name="TEXT">Fire Danger</field></shadow><block type="str_format_float" id="`+}w,O*uI]-eZLiAw-tU"><field name="D">1</field><field name="W">4</field><value name="VALUE"><block type="variables_get" id="zy`FD[mQc:oqx?sW_$zg"><field name="VAR" id="ABC9sGviU5x;BeYi~ZvF">temperature</field></block></value></block></value><value name="X"><shadow type="math_number" id="MRwL.q;;z+Ut7g5e*kNX"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="d)Q@:u4cX6jV.(I1cvC/"><field name="NUM">34</field></shadow></value><value name="C"><shadow type="math_number" id="nDudL`66|Rz,*zAXK(Pz"><field name="NUM">1</field></shadow></value><next><block type="display_text" id="M9A}Id*O~R^HgX@dw*]r"><value name="VALUE"><shadow type="text" id="VW[*YfNn[n2#nMHZ;3t-"><field name="TEXT">Fire Danger</field></shadow><block type="text" id="v4UBbvi2`z$V6GvOsaP)"><field name="TEXT">C</field></block></value><value name="X"><shadow type="math_number" id="ZtWHi5{J:%3A:vUqrUo}"><field name="NUM">50</field></shadow></value><value name="Y"><shadow type="math_number" id="98x!-qM0Q#7]P[kkV$9B"><field name="NUM">34</field></shadow></value><value name="C"><shadow type="math_number" id="H01Den#=xfcdlcrN0Xv4"><field name="NUM">1</field></shadow></value><next><block type="display_setfont" id="ViYQ)koYEiv$w]}7Ap9k"><field name="FONT">mono8x8</field><next><block type="display_text" id="mNP}8O@@^4om`6RGOAEr"><value name="VALUE"><shadow type="text" id="dk/w5!(D=u]/tIWUV_,f"><field name="TEXT">Fire Danger</field></shadow><block type="variables_get" id="zE,]:)|*sE1eO0+J!ox:"><field name="VAR" id="s~%TQ81?L-3aRx!u?kbx">danger</field></block></value><value name="X"><shadow type="math_number" id="l3Asos:l{Gui0e5}D-n#"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="/,x.SNM;KbFLidBQ)!_c"><field name="NUM">44</field></shadow></value><value name="C"><shadow type="math_number" id="x`rJK-!7G?MVqtn!@tr."><field name="NUM">1</field></shadow></value><next><block type="display_text" id="CD1%sw9(9Gb__U#?kP6j"><value name="VALUE"><shadow type="text" id="-pUS=-?k[~l~8v}4#4Cg"><field name="TEXT">A - exit</field></shadow></value><value name="X"><shadow type="math_number" id="YLh#h,nLVKVHztnM]jLR"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="[1~Xb!Z%?*Cl|S8gc~.a"><field name="NUM">63</field></shadow></value><value name="C"><shadow type="math_number" id="_n-.dh@NMHgc=~mJ*,2J"><field name="NUM">1</field></shadow></value><next><block type="display_show" id="MaFDqF]Sn/9m(=bf]4a^"></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block><block type="event_every_seconds" id="t,dItd{$^re)/wgWV-UZ" x="390" y="-130"><field name="T">2</field><statement name="DO"><block type="variables_set" id="Msys4{Bq$x{oq,bS8Iqt"><field name="VAR" id="ABC9sGviU5x;BeYi~ZvF">temperature</field><value name="VALUE"><block type="onewire_ds18_read_temp_v2" id="$)%.v7x2dS9zv9A:cn]K"><value name="PIN"><block type="pin_selector_sensor" id="}-i)[yhU8!?V-2E(49v^"><field name="PIN">"P2"</field></block></value></block></value><next><block type="controls_if" id="LFk1RW^MDSODmjV-X^DP"><mutation elseif="2" else="1"></mutation><value name="IF0"><block type="logic_compare" id="~{Z~u2gc9gg$rvH/%Vor"><field name="OP">LT</field><value name="A"><block type="variables_get" id="XD7uYMAAxlG;x){3!^eu"><field name="VAR" id="ABC9sGviU5x;BeYi~ZvF">temperature</field></block></value><value name="B"><block type="math_number" id="c^VUmxrodh=gRhNg]s|+"><field name="NUM">25</field></block></value></block></value><statement name="DO0"><block type="servo_angle" id="1i2kvrF5TWGI~Ga2c$/0"><field name="PIN">P1</field><value name="ANGLE"><shadow type="math_number" id="JM6{X/l1.cr9v,C$Pk@8"><field name="NUM">60</field></shadow></value><next><block type="variables_set" id="s:90-/;l~qe,`Evw=YiU"><field name="VAR" id="s~%TQ81?L-3aRx!u?kbx">danger</field><value name="VALUE"><block type="text" id="b@blfIH):@9=],?qKKs$"><field name="TEXT">Moderate</field></block></value></block></next></block></statement><value name="IF1"><block type="logic_compare" id="q#dR;MG#Q|zWlOv@;eux"><field name="OP">LT</field><value name="A"><block type="variables_get" id="F[~Xp1!2H)_eHUWMonmC"><field name="VAR" id="ABC9sGviU5x;BeYi~ZvF">temperature</field></block></value><value name="B"><block type="math_number" id="L1/OEzrzT(W9sA0?V?NI"><field name="NUM">30</field></block></value></block></value><statement name="DO1"><block type="servo_angle" id="+ho=+{Y8z%Oq0iwt?@-F"><field name="PIN">P1</field><value name="ANGLE"><shadow type="math_number" id=";Orr$i:a,K;$A3pG$s_!"><field name="NUM">25</field></shadow></value><next><block type="variables_set" id="hfZ8V7(Z^*/NKiL!28kK"><field name="VAR" id="s~%TQ81?L-3aRx!u?kbx">danger</field><value name="VALUE"><block type="text" id="p,(R:+DH8|Xn_*pjDrEw"><field name="TEXT">High</field></block></value></block></next></block></statement><value name="IF2"><block type="logic_compare" id=".~^g_*5W{NPYeqtpO-44"><field name="OP">LT</field><value name="A"><block type="variables_get" id="LU8Jzt~?9}Fa~FIerUt:"><field name="VAR" id="ABC9sGviU5x;BeYi~ZvF">temperature</field></block></value><value name="B"><block type="math_number" id="vJ16{W.D%T6m4Z|ar(g$"><field name="NUM">35</field></block></value></block></value><statement name="DO2"><block type="servo_angle" id="d:N:8(S^+-cfbxpLdDG4"><field name="PIN">P1</field><value name="ANGLE"><shadow type="math_number" id="/PMllZM|Kx7EZL_-O}.9"><field name="NUM">-25</field></shadow></value><next><block type="variables_set" id="[S[P$B[[qElvty.:Wl#-"><field name="VAR" id="s~%TQ81?L-3aRx!u?kbx">danger</field><value name="VALUE"><block type="text" id="(h74k7(LuoiDn,CN#e0q"><field name="TEXT">Extreme</field></block></value></block></next></block></statement><statement name="ELSE"><block type="servo_angle" id="Ttt{I#iZ(jb6@#`~;}l{"><field name="PIN">P1</field><value name="ANGLE"><shadow type="math_number" id="*HrtZk(;VA)e*qsa{hih"><field name="NUM">-60</field></shadow></value><next><block type="variables_set" id="g!!q7!n`oc4@Lu:~M#5P"><field name="VAR" id="s~%TQ81?L-3aRx!u?kbx">danger</field><value name="VALUE"><block type="text" id="*{L0Xx,cbuY=xoTSfGKP"><field name="TEXT">Catastrophic</field></block></value></block></next></block></statement></block></next></block></statement></block><block type="event_button_was_pressed" id="?TX2l=@dBA8chPM1_]^u" x="390" y="370"><field name="BUTTON">kooka.button_a.was_pressed()</field><statement name="DO"><block type="exit_program" id="c4~Uq$|TsY8|R2r$foI!"></block></statement></block></xml>
