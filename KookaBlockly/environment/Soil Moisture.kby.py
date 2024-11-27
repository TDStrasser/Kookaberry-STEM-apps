import machine, kooka
import time
import fonts
from machine import ADC

x = None
y = None
width = None
height = None
value = None
vert = None
reading = None
dry = None
wet = None
bar_scaled = None

# Describe this function...
def bargraph(x, y, width, height, value, vert):
    global reading, dry, wet, bar_scaled
    kooka.display.rect(int(x), int(y), int(width), int(height), 1)
    if vert:
        bar_scaled = (value / 100) * height
        kooka.display.fill_rect(int(x), int((y + height) - bar_scaled), int(width), int(bar_scaled), 1)
    else:
        bar_scaled = (value / 100) * width
        kooka.display.fill_rect(int(x), int(y), int(bar_scaled), int(height), 1)

# Describe this function...
def LEDs(reading):
    global x, y, width, height, value, vert, dry, wet, bar_scaled
    if reading <= 33:
        kooka.led_red.on()
    else:
        kooka.led_red.off()
    if reading > 33 and reading < 67:
        kooka.led_orange.on()
    else:
        kooka.led_orange.off()
    if reading >= 67:
        kooka.led_green.on()
    else:
        kooka.led_green.off()



kooka.display.show()

# Initialise timer counters.
_timer500 = time.ticks_ms()

# On-start code, run once at start-up.
if True:
    reading = 0
    dry = 0
    wet = 3.3

# Main loop code, run continuously.
while True:
    if time.ticks_diff(time.ticks_ms(), _timer500) >= 0:
        _timer500 += 500
        if dry - wet != 0:
            reading = ((dry - ADC("P1").read_u16() / 65535 * 3.3) / (dry - wet) * 100)
        kooka.display.fill(0)
        kooka.display.setfont(fonts.mono8x8)
        kooka.display.print('Soil Moisture', show=0)
        kooka.display.print('Value % =', "{:5.1f}".format(reading), show=0)
        bargraph(10, 20, 100, 10, reading, 0)
        kooka.display.text(str('A-exit'), int(0), int(63), int(1))
        kooka.display.text(str('Cal: C-dry D-wet'), int(0), int(50), int(1))
        kooka.display.setfont(fonts.mono6x7)
        kooka.display.text(str('Conn Sensor to P1'), int(0), int(40), int(1))
        kooka.display.show()
        LEDs(reading)
    if kooka.button_a.was_pressed():
        raise SystemExit
    if kooka.button_c.was_pressed():
        dry = ADC("P1").read_u16() / 65535 * 3.3
    if kooka.button_d.was_pressed():
        wet = ADC("P1").read_u16() / 65535 * 3.3
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="$R_,@JR4N|hB#z/%$U7Z">x</variable><variable id="gg9C:xQn7l8IL-U1[M/;">y</variable><variable id="XBsys=dGA%QO-*!]C/Df">width</variable><variable id="HwN8{q2,@=oqAC`1B)U9">height</variable><variable id="L/jujykYj_ME{exvcCZ]">value</variable><variable id="+a4CH]{wED=`0eZ~;Qn/">vert</variable><variable id="CDBNB}XY~mz3*ow/FgT$">reading</variable><variable id="!~BQ]~te3O_J0,JP)rd6">dry</variable><variable id="rIa{J^7..p4GKuqI;2z5">wet</variable><variable id="Ih2T_Omv7]A(X@)gKm#|">bar_scaled</variable></variables><block type="event_on_start" id="^ut)wtaARW*LWejB~u0!" x="-170" y="-330"><statement name="DO"><block type="variables_set" id="WkPkx.M;/@9Xs%Z[3eD|"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field><value name="VALUE"><block type="math_number" id="DFbN3c6HlWk`|Yfvh@:`"><field name="NUM">0</field></block></value><next><block type="variables_set" id="5HX=*h_=sci2Aqmo5}01"><field name="VAR" id="!~BQ]~te3O_J0,JP)rd6">dry</field><value name="VALUE"><block type="math_number" id="8ynY%Q$UR.bkf*T}vTWL"><field name="NUM">0</field></block></value><next><block type="variables_set" id="l|ct81U+1byp}5^i/*hv"><field name="VAR" id="rIa{J^7..p4GKuqI;2z5">wet</field><value name="VALUE"><block type="math_number" id="G|kY3!1|,Z-G5*[;{A.L"><field name="NUM">3.3</field></block></value></block></next></block></next></block></statement></block><block type="event_every_seconds" id="}X@~88Kw*^4.z7k9ETwk" x="170" y="-310"><field name="T">0.5</field><statement name="DO"><block type="controls_if" id=";)[?BG/GhL@)a3HuBYw/"><value name="IF0"><block type="logic_compare" id="KMKlvT4n|iPatUFwDp{X"><field name="OP">NEQ</field><value name="A"><block type="math_arithmetic" id="gv{4LvNt.uhS~RInzt6t"><field name="OP">MINUS</field><value name="A"><shadow type="math_number" id="Z#QA~SE-X(@04`MBB]`7"><field name="NUM">1</field></shadow><block type="variables_get" id=";ejR?Wy1m7-g)]LG)s9{"><field name="VAR" id="!~BQ]~te3O_J0,JP)rd6">dry</field></block></value><value name="B"><shadow type="math_number" id="Ry-(lN]|:-Jx[@ENE*bQ"><field name="NUM">1</field></shadow><block type="variables_get" id="iyUxd(SXir,Athx!35Sa"><field name="VAR" id="rIa{J^7..p4GKuqI;2z5">wet</field></block></value></block></value><value name="B"><block type="math_number" id="%`?B;Nvqjd#6G|eUWVvM"><field name="NUM">0</field></block></value></block></value><statement name="DO0"><block type="variables_set" id="L`[9KuKceqckjR@hMHAF"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field><value name="VALUE"><block type="soil_moisture_read" id="pgMo7t2_h2u~%Mas.|Ql"><field name="PIN">P1</field><value name="DRY"><shadow type="math_number"><field name="NUM">0</field></shadow><block type="variables_get" id=",*3{^b23FDLFI2,sE71,"><field name="VAR" id="!~BQ]~te3O_J0,JP)rd6">dry</field></block></value><value name="WET"><shadow type="math_number"><field name="NUM">3.3</field></shadow><block type="variables_get" id="vV5`s`W[[qqmCH]@U#g}"><field name="VAR" id="rIa{J^7..p4GKuqI;2z5">wet</field></block></value></block></value></block></statement><next><block type="display_clear" id="+9EB,JS771CbW`[Xy/i?"><next><block type="display_setfont" id="^eDK$$}yuVqKK.wVKI$s"><field name="FONT">mono8x8</field><next><block type="display_print" id=";y5x5a}rZ*8%ybm8VCkG"><value name="VALUE"><shadow type="text" id="LyjaMJl}ny1mHWq.(5eq"><field name="TEXT">Soil Moisture</field></shadow></value><next><block type="display_print2" id="GILnw-Xv}S}Y$#12=K9a"><value name="VALUE1"><shadow type="text" id="#NK+g4FeXF!B3$83|^z("><field name="TEXT">Value % =</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="`kKt0lII2vfou!d}Spa%"><field name="NUM">123</field></shadow><block type="str_format_float" id="%UNuZ{TPk7.:p8.Z/sY6"><field name="D">1</field><field name="W">5</field><value name="VALUE"><block type="variables_get" id="]6b2YFsQc[b%D8yc27B="><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field></block></value></block></value><next><block type="procedures_callnoreturn" id="m//v+Ys=KtCIUma0cEba"><mutation name="bargraph"><arg name="x"></arg><arg name="y"></arg><arg name="width"></arg><arg name="height"></arg><arg name="value"></arg><arg name="vert"></arg></mutation><value name="ARG0"><block type="math_number" id="%mE6GNzZqSnRBD5cE}tO"><field name="NUM">10</field></block></value><value name="ARG1"><block type="math_number" id="w?B~e(rrCiNfIMwAwq=:"><field name="NUM">20</field></block></value><value name="ARG2"><block type="math_number" id="WO;$[gIRbB,ba_|w:cc@"><field name="NUM">100</field></block></value><value name="ARG3"><block type="math_number" id="yDw!K;k^7cgw]xVKDzv{"><field name="NUM">10</field></block></value><value name="ARG4"><block type="variables_get" id="=Q$`=BDfm)%I[^,*r/WU"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field></block></value><value name="ARG5"><block type="math_number" id="N!jd]$q$#MI+*tDNmFsA"><field name="NUM">0</field></block></value><next><block type="display_text" id="sL*UnyzR9GyH{E1B7)x/"><value name="VALUE"><shadow type="text" id="RIc|^C^;ktBfg44uk[{s"><field name="TEXT">A-exit</field></shadow></value><value name="X"><shadow type="math_number" id="?+4c!|qd?]WgSN{?4V{D"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="]T6i#i71]jALvVY$K`C#"><field name="NUM">63</field></shadow></value><value name="C"><shadow type="math_number" id="u;5/wxXpiaoveX)ymZzk"><field name="NUM">1</field></shadow></value><next><block type="display_text" id="1D{:Cj2REC*C{uEHSLc%"><value name="VALUE"><shadow type="text" id="_Wi!T)atVqGB.8``.z}z"><field name="TEXT">Cal: C-dry D-wet</field></shadow></value><value name="X"><shadow type="math_number" id="!P5Yox=u4*c5xwqfZ$wZ"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="_KV)]k0h?x^kqqQ:u6PG"><field name="NUM">50</field></shadow></value><value name="C"><shadow type="math_number" id="=(V:-y/iXbZFI;:%_[N|"><field name="NUM">1</field></shadow></value><next><block type="display_setfont" id=":hE5FU-6WI+gYt`8aL%/"><field name="FONT">mono6x7</field><next><block type="display_text" id="w-sH?oZ;mY?-,ZObsyh|"><value name="VALUE"><shadow type="text" id="Ul+,*2%aQ];WM#+rzISE"><field name="TEXT">Conn Sensor to P1</field></shadow></value><value name="X"><shadow type="math_number" id="C|HoAav%@jL*|v1$~fKK"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="l%x0Wz[CPd^SI8O@YC?L"><field name="NUM">40</field></shadow></value><value name="C"><shadow type="math_number" id="X=sFhaKX#ZDR~J!.3.OL"><field name="NUM">1</field></shadow></value><next><block type="display_show" id="quHf$i*k.npGtX.kWjRD"><next><block type="procedures_callnoreturn" id="0]mOOw7UWv6^C?5t!F3-"><mutation name="LEDs"><arg name="reading"></arg></mutation><value name="ARG0"><block type="variables_get" id="/UFpRedbEK=Jmc.Bsn;p"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field></block></value></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block><block type="procedures_defnoreturn" id="^YDH~:)dPYyY{[8-|IW:" x="910" y="-310"><mutation><arg name="x" varid="$R_,@JR4N|hB#z/%$U7Z"></arg><arg name="y" varid="gg9C:xQn7l8IL-U1[M/;"></arg><arg name="width" varid="XBsys=dGA%QO-*!]C/Df"></arg><arg name="height" varid="HwN8{q2,@=oqAC`1B)U9"></arg><arg name="value" varid="L/jujykYj_ME{exvcCZ]"></arg><arg name="vert" varid="+a4CH]{wED=`0eZ~;Qn/"></arg></mutation><field name="NAME">bargraph</field><comment pinned="false" h="80" w="160">Describe this function...</comment><statement name="STACK"><block type="display_rect" id="X]ODPflaV[*GlkJ]yG^K"><field name="F">FALSE</field><value name="X"><shadow type="math_number" id="?CH06H^(}K9dR^;LvUz7"><field name="NUM">10</field></shadow><block type="variables_get" id="A$Zpgp7u/iNC$WoByN2K"><field name="VAR" id="$R_,@JR4N|hB#z/%$U7Z">x</field></block></value><value name="Y"><shadow type="math_number" id="Gc/AVkv9;K+5Q+tnK8-$"><field name="NUM">25</field></shadow><block type="variables_get" id=")=6vz{r4p/lj@,.(L*(!"><field name="VAR" id="gg9C:xQn7l8IL-U1[M/;">y</field></block></value><value name="W"><shadow type="math_number" id="X*zo1@.b-)$%eVWkq.Q/"><field name="NUM">20</field></shadow><block type="variables_get" id="U5`OX?wgy(aKyNTUr;lx"><field name="VAR" id="XBsys=dGA%QO-*!]C/Df">width</field></block></value><value name="H"><shadow type="math_number" id="q@P;}:ik@5,Py4)3F*1L"><field name="NUM">35</field></shadow><block type="variables_get" id="LvSr+D}mu0]@pi~N;pMa"><field name="VAR" id="HwN8{q2,@=oqAC`1B)U9">height</field></block></value><next><block type="controls_if" id="aWG8`sY)uH}nmP(5+9w7"><mutation else="1"></mutation><value name="IF0"><block type="variables_get" id="Kfs+[OdzAoyLqi.|d/th"><field name="VAR" id="+a4CH]{wED=`0eZ~;Qn/">vert</field></block></value><statement name="DO0"><block type="variables_set" id="|UY,4FQ~1%/)%hrWew(S"><field name="VAR" id="Ih2T_Omv7]A(X@)gKm#|">bar_scaled</field><value name="VALUE"><block type="math_arithmetic" id="=+a$`@$o1cFYVYFC]aV9"><field name="OP">MULTIPLY</field><value name="A"><shadow type="math_number" id="0AwLGPOVJBIb/hTe_ITc"><field name="NUM">1</field></shadow><block type="math_arithmetic" id="1a6]b$#MFYBKVhflFzT="><field name="OP">DIVIDE</field><value name="A"><shadow type="math_number" id="^}E]xt(uE0NuQmQ#VjbI"><field name="NUM">1</field></shadow><block type="variables_get" id="_w*2e5A}}o(R,M8X(7-J"><field name="VAR" id="L/jujykYj_ME{exvcCZ]">value</field></block></value><value name="B"><shadow type="math_number" id="O)|$$V9^^V~{pcM6o,ks"><field name="NUM">100</field></shadow></value></block></value><value name="B"><shadow type="math_number" id="kd-@CxRJ8!v:Q?|:C(Ag"><field name="NUM">1</field></shadow><block type="variables_get" id="XLWgdl9u:Qs$q|5c+_a1"><field name="VAR" id="HwN8{q2,@=oqAC`1B)U9">height</field></block></value></block></value><next><block type="display_rect" id=".?E!R4+k3)$yzz]7(HWG"><field name="F">TRUE</field><value name="X"><shadow type="math_number" id="ZScE,quwtvRduv}`}Q=r"><field name="NUM">10</field></shadow><block type="variables_get" id="QfV0i.K$)!Aln1@^r!}J"><field name="VAR" id="$R_,@JR4N|hB#z/%$U7Z">x</field></block></value><value name="Y"><shadow type="math_number" id=".B|:Ql`S8e2Hm?F$/DYS"><field name="NUM">25</field></shadow><block type="math_arithmetic" id="D^W?;kRyVk-Tu]USSSO1"><field name="OP">MINUS</field><value name="A"><shadow type="math_number" id="k_g~$*{Pc|]d2/nqc~ex"><field name="NUM">1</field></shadow><block type="math_arithmetic" id="F5r5xY)ANwQ4OCo|Z~=/"><field name="OP">ADD</field><value name="A"><shadow type="math_number" id="?xWy@NDzyK)kHy=RUck@"><field name="NUM">1</field></shadow><block type="variables_get" id="?Gw#YzQY0dNGIkCvxv)}"><field name="VAR" id="gg9C:xQn7l8IL-U1[M/;">y</field></block></value><value name="B"><shadow type="math_number" id="?a_/?47`Q:LK8RB~(+Fk"><field name="NUM">1</field></shadow><block type="variables_get" id="D|#GIwi{6+7kt!ynS:ZL"><field name="VAR" id="HwN8{q2,@=oqAC`1B)U9">height</field></block></value></block></value><value name="B"><shadow type="math_number" id="4^/k.O~-v*f:|0$`XMMl"><field name="NUM">1</field></shadow><block type="variables_get" id="rM7yA7y`;2zi8aSq,g5R"><field name="VAR" id="Ih2T_Omv7]A(X@)gKm#|">bar_scaled</field></block></value></block></value><value name="W"><shadow type="math_number" id="nm1hn5D{FiiB}?^0raRR"><field name="NUM">20</field></shadow><block type="variables_get" id="ZfKgBDza9j=L9F+}1J!R"><field name="VAR" id="XBsys=dGA%QO-*!]C/Df">width</field></block></value><value name="H"><shadow type="math_number" id="2Qa#(ZPh5j6(bMS8$2T`"><field name="NUM">20</field></shadow><block type="variables_get" id="Y/_1EU[aqyVD4yHB0Pzv"><field name="VAR" id="Ih2T_Omv7]A(X@)gKm#|">bar_scaled</field></block></value></block></next></block></statement><statement name="ELSE"><block type="variables_set" id="hsIqrt3K[ULr^:uA%p@V"><field name="VAR" id="Ih2T_Omv7]A(X@)gKm#|">bar_scaled</field><value name="VALUE"><block type="math_arithmetic" id="[pZ3|n4mpmiuvv2w(Zz["><field name="OP">MULTIPLY</field><value name="A"><shadow type="math_number" id=".E`!E:M/`Qz/Xb~`BMYs"><field name="NUM">1</field></shadow><block type="math_arithmetic" id="+M+6JJA4dCGcph*Py+Jc"><field name="OP">DIVIDE</field><value name="A"><shadow type="math_number"><field name="NUM">1</field></shadow><block type="variables_get" id="EXE10smWbwiuBK[Ww3Ub"><field name="VAR" id="L/jujykYj_ME{exvcCZ]">value</field></block></value><value name="B"><shadow type="math_number" id="AwO7:.sqMEl(E79[^Ok2"><field name="NUM">100</field></shadow></value></block></value><value name="B"><shadow type="math_number"><field name="NUM">1</field></shadow><block type="variables_get" id="4t!nE3D)FB]ZBD_r5AC%"><field name="VAR" id="XBsys=dGA%QO-*!]C/Df">width</field></block></value></block></value><next><block type="display_rect" id=".Bl%;{,dY8?BZ|6HDr8E"><field name="F">TRUE</field><value name="X"><shadow type="math_number"><field name="NUM">10</field></shadow><block type="variables_get" id="{TedGX}SxWY|gD!IuY~("><field name="VAR" id="$R_,@JR4N|hB#z/%$U7Z">x</field></block></value><value name="Y"><shadow type="math_number" id="lXN|feusAE=QWpq^)6b^"><field name="NUM">25</field></shadow><block type="variables_get" id="87+3,aL1P{8b1PR!wgHh"><field name="VAR" id="gg9C:xQn7l8IL-U1[M/;">y</field></block></value><value name="W"><shadow type="math_number" id="[Q%W,[8r;Bf!F8K9!{p:"><field name="NUM">20</field></shadow><block type="variables_get" id="oy}|IN/?0nd|mRb8!O:n"><field name="VAR" id="Ih2T_Omv7]A(X@)gKm#|">bar_scaled</field></block></value><value name="H"><shadow type="math_number" id="LPbi3TA0f|h@.[.V$H%c"><field name="NUM">20</field></shadow><block type="variables_get" id="/63lnCMsv92?=8mXP(#z"><field name="VAR" id="HwN8{q2,@=oqAC`1B)U9">height</field></block></value></block></next></block></statement></block></next></block></statement></block><block type="event_button_was_pressed" id="-DrA8Q.?TcD01h-IwtD1" x="-170" y="-70"><field name="BUTTON">kooka.button_a.was_pressed()</field><statement name="DO"><block type="exit_program" id="C?-)/(q1KdM9wD*$}=ZL"></block></statement></block><block type="event_button_was_pressed" id="%Ie7SQ;#ly%31uA4)}AJ" x="-170" y="50"><field name="BUTTON">kooka.button_c.was_pressed()</field><statement name="DO"><block type="variables_set" id="^`8OL^|9DhON3*DB(wGa"><field name="VAR" id="!~BQ]~te3O_J0,JP)rd6">dry</field><value name="VALUE"><block type="adc_read_v" id="FR8rM5M.=+9/SkYTHnud"><field name="PIN">P1</field></block></value></block></statement></block><block type="event_button_was_pressed" id=";g`tguJcIjsl{rC_D:25" x="-170" y="150"><field name="BUTTON">kooka.button_d.was_pressed()</field><statement name="DO"><block type="variables_set" id="9(:Neoone5}tcss1.$Q5"><field name="VAR" id="rIa{J^7..p4GKuqI;2z5">wet</field><value name="VALUE"><block type="adc_read_v" id="$EtA=qVQs6PNc_UWGKi$"><field name="PIN">P1</field></block></value></block></statement></block><block type="procedures_defnoreturn" id="K},SC#d}^~kan%4]IimG" x="890" y="330"><mutation><arg name="reading" varid="CDBNB}XY~mz3*ow/FgT$"></arg></mutation><field name="NAME">LEDs</field><comment pinned="false" h="80" w="160">Describe this function...</comment><statement name="STACK"><block type="controls_if" id="NS)QQV,B[1Ht*@93,aIa"><mutation else="1"></mutation><value name="IF0"><block type="logic_compare" id="/qduMjPoj]LsdZu0OqV;"><field name="OP">LTE</field><value name="A"><block type="variables_get" id="h-Abk3Al}/w1(3~GY2]M"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field></block></value><value name="B"><block type="math_number" id="8GdB8AlLy-BdXI[=ZuCO"><field name="NUM">33</field></block></value></block></value><statement name="DO0"><block type="led_on" id="BltE~/D0$Ew3Jaae-.G:"><field name="LED">led_red</field></block></statement><statement name="ELSE"><block type="led_off" id="jsxFUj}ZJmntUc!TUT5m"><field name="LED">led_red</field></block></statement><next><block type="controls_if" id="yvuH`[3J0AEab/km8:B="><mutation else="1"></mutation><value name="IF0"><block type="logic_operation" id="I:Sc4SU@R1|Ijg{@p}Kc"><field name="OP">AND</field><value name="A"><block type="logic_compare" id="M,kkHAWtn:+Z*(Z#L83X"><field name="OP">GT</field><value name="A"><block type="variables_get" id="(/85J_C9T@4!IE]EP;n6"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field></block></value><value name="B"><block type="math_number" id=".tAcia*YHjO_WbC/pNnf"><field name="NUM">33</field></block></value></block></value><value name="B"><block type="logic_compare" id="Cf;{G6h:1h_kg%%KIgj["><field name="OP">LT</field><value name="A"><block type="variables_get" id="^Y)^[cc-6x_;JQ(@$#.*"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field></block></value><value name="B"><block type="math_number" id="RGGxo-`2h-w}W_jG4FEF"><field name="NUM">67</field></block></value></block></value></block></value><statement name="DO0"><block type="led_on" id=")P*tyPoXB3bKgM+(Byz:"><field name="LED">led_orange</field></block></statement><statement name="ELSE"><block type="led_off" id="t;#jWZg4^t;YyGatM6,J"><field name="LED">led_orange</field></block></statement><next><block type="controls_if" id="[fy@gsqVgJ17F^rz]q!-"><mutation else="1"></mutation><value name="IF0"><block type="logic_compare" id="XtRN=J=y,`!#Lp@^^+op"><field name="OP">GTE</field><value name="A"><block type="variables_get" id="9xkC~Tm|.~9j1:`M#5h2"><field name="VAR" id="CDBNB}XY~mz3*ow/FgT$">reading</field></block></value><value name="B"><block type="math_number" id="C5aSGAP^EGKa)EP_!gIX"><field name="NUM">67</field></block></value></block></value><statement name="DO0"><block type="led_on" id="1ZkItU?R,t%?Ns=]-m+a"><field name="LED">led_green</field></block></statement><statement name="ELSE"><block type="led_off" id="QJo~u?dp7zfwkU*)z2XN"><field name="LED">led_green</field></block></statement></block></next></block></next></block></statement></block></xml>
