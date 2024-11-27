import machine, kooka
import time
import fonts
from machine import Pin

pulse_timer = None
last_input = None
pulse_input = None
speed = None
select_sensor = None
temperature = None
humidity = None
last_speed = None

def time_ms():
    return time.time() * 1000 + machine.RTC().datetime()[-1] // 1000

def dht_measure(variant, pin):
    import dht
    dht = getattr(dht, variant)(pin)
    dht.measure()
    return dht


pulse_timer = time_ms()
last_input = False
speed = 0
select_sensor = False
kooka.display.clear()
kooka.display.print('Initialising...', show=0)
kooka.display.show()
temperature = dht_measure("DHT11", "P1").temperature()
time.sleep(1)
humidity = dht_measure("DHT11", "P1").humidity()
time.sleep(1)

kooka.display.show()

# Initialise timer counters.
_timer10000 = time.ticks_ms()
_timer1000 = time.ticks_ms()

# Main loop code, run continuously.
while True:
    pulse_input = Pin("P2", Pin.IN).value()
    if pulse_input and not last_input:
        pulse_timer = time_ms()
        last_input = True
        kooka.led_orange.on()
    elif last_input and not pulse_input:
        last_input = False
        speed = 31 / (time_ms() - pulse_timer)
        kooka.led_orange.off()
    if time.ticks_diff(time.ticks_ms(), _timer10000) >= 0:
        _timer10000 += 10000
        if select_sensor:
            temperature = dht_measure("DHT11", "P1").temperature()
        else:
            humidity = dht_measure("DHT11", "P1").humidity()
        select_sensor = not select_sensor
    if time.ticks_diff(time.ticks_ms(), _timer1000) >= 0:
        _timer1000 += 1000
        kooka.display.clear()
        kooka.display.print('Weather', show=0)
        kooka.display.setfont(fonts.mono8x13)
        kooka.display.print(temperature, 'C', show=0)
        kooka.display.print(humidity, '% Rel Humid', show=0)
        kooka.display.print("{:4.2f}".format(speed), 'm/s Wind', show=0)
        last_speed = speed
        if speed == last_speed:
            speed = 0
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="Gw!BPYM~_;Y_6FB0_ZEB">pulse_timer</variable><variable id="0k=_|!W:y2]Y=D3XpjQ`">last_input</variable><variable id="5Td7r8uEJF$S)W=Tup;s">pulse_input</variable><variable id="wgh23U+#tXJ{]nr3x^Pr">speed</variable><variable id="/#n%@ZmEvlCC(k!2G:Bt">select_sensor</variable><variable id="]|-(Rrj`E*/yCa~uoOG1">temperature</variable><variable id=":il)3u?aiD*~+Aj;Ys^T">humidity</variable><variable id="=AkE,RvMF/le:}G~I3.s">last_speed</variable></variables><block type="variables_set" id="$^ah17f`S+00l+Zc6ps`" x="170" y="-130"><field name="VAR" id="Gw!BPYM~_;Y_6FB0_ZEB">pulse_timer</field><value name="VALUE"><block type="time_time_ms" id=":(uCp3|#-)/pH;!O7g:V"></block></value><next><block type="variables_set" id="5r[NG)ytU;,4CR+twb$L"><field name="VAR" id="0k=_|!W:y2]Y=D3XpjQ`">last_input</field><value name="VALUE"><block type="logic_boolean" id="5]*e+[w-wPA_|6Gn}$$m"><field name="BOOL">FALSE</field></block></value><next><block type="variables_set" id="hN#%2R-{Zf`Esp~60Rp7"><field name="VAR" id="wgh23U+#tXJ{]nr3x^Pr">speed</field><value name="VALUE"><block type="math_number" id="yvN$w96Pw9Lj!ShQj?NM"><field name="NUM">0</field></block></value><next><block type="variables_set" id="#7;FWT7b6Psl.aI+7_0{"><field name="VAR" id="/#n%@ZmEvlCC(k!2G:Bt">select_sensor</field><value name="VALUE"><block type="logic_boolean" id=":~`}ap!ziuIChFc}4^OI"><field name="BOOL">FALSE</field></block></value><next><block type="display_clear" id="GhV}3$|#@oekx3xA|s3n"><next><block type="display_print" id="mBDu!b=ef?PD{;:n|4TL"><value name="VALUE"><shadow type="text" id=":tpry7p(AyRd=c2X]$s4"><field name="TEXT">Initialising...</field></shadow></value><next><block type="display_show" id=";h#jZdV^},,y-o7r$/0J"><next><block type="variables_set" id="D-y=pT_A0W*1U5bnH~SK"><field name="VAR" id="]|-(Rrj`E*/yCa~uoOG1">temperature</field><value name="VALUE"><block type="dht_read" id="24^-T.~a]=N*N{@=?Bm7"><field name="PROPERTY">temperature</field><field name="VARIANT">DHT11</field><field name="PIN">P1</field></block></value><next><block type="time_sleep" id="ehrcwZ[Fn?B!QPRh:o]s"><value name="VALUE"><shadow type="math_number" id="dm[,a*rlHi-rM*a]r.=A"><field name="NUM">1</field></shadow></value><next><block type="variables_set" id="dAQQtJdITKSdVhMKb+Kw"><field name="VAR" id=":il)3u?aiD*~+Aj;Ys^T">humidity</field><value name="VALUE"><block type="dht_read" id="3EY,~jmL2*Xo1KN`ur|F"><field name="PROPERTY">humidity</field><field name="VARIANT">DHT11</field><field name="PIN">P1</field></block></value><next><block type="time_sleep" id="3UvATADZg{*|O/RH_l-k"><value name="VALUE"><shadow type="math_number" id=".xM4FWEXNLxdBHP~odCH"><field name="NUM">1</field></shadow></value></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block><block type="event_every_seconds" id="7,[haNB[T!4Iy{/-KA)j" x="770" y="-150"><field name="T">10</field><statement name="DO"><block type="controls_if" id="YzyOm(adUWO~#E6pW_8)"><mutation else="1"></mutation><value name="IF0"><block type="variables_get" id="(SAKj-+K*{pG6kifp)u4"><field name="VAR" id="/#n%@ZmEvlCC(k!2G:Bt">select_sensor</field></block></value><statement name="DO0"><block type="variables_set" id="_oLNx0z9LCX(xtvQMk#{"><field name="VAR" id="]|-(Rrj`E*/yCa~uoOG1">temperature</field><value name="VALUE"><block type="dht_read" id="[BI_)W$.=CW:yC-Mb9@R"><field name="PROPERTY">temperature</field><field name="VARIANT">DHT11</field><field name="PIN">P1</field></block></value></block></statement><statement name="ELSE"><block type="variables_set" id="c4m+f(F)ZrUQfMIlRc;E"><field name="VAR" id=":il)3u?aiD*~+Aj;Ys^T">humidity</field><value name="VALUE"><block type="dht_read" id="XYaP;]1[[J,D+@lD?-uh"><field name="PROPERTY">humidity</field><field name="VARIANT">DHT11</field><field name="PIN">P1</field></block></value></block></statement><next><block type="variables_set" id="tkV,ig+I;aUvCIe[0Y3,"><field name="VAR" id="/#n%@ZmEvlCC(k!2G:Bt">select_sensor</field><value name="VALUE"><block type="logic_negate" id="S0j8o9c,IcOdP9slwxBT"><value name="BOOL"><block type="variables_get" id="n7ZC^fEzv))F4FOa(2tS"><field name="VAR" id="/#n%@ZmEvlCC(k!2G:Bt">select_sensor</field></block></value></block></value></block></next></block></statement></block><block type="event_every_seconds" id="nInesBo0zRaIL)I0`:r1" x="790" y="50"><field name="T">1</field><statement name="DO"><block type="display_clear" id="iFNyt6_LL}ZR`PczS=%u"><next><block type="display_print" id=",`l.H[7pLsq8Q,CkaTt4"><value name="VALUE"><shadow type="text" id="gu+9J6e.Q}Q@tpJc9n:3"><field name="TEXT">Weather</field></shadow></value><next><block type="display_setfont" id="Vv^1d@Iut{at%@h0`lVK"><field name="FONT">mono8x13</field><next><block type="display_print2" id="!jU7vr)]o^${:MXg_V!:"><value name="VALUE1"><shadow type="text" id="O.=Mt1%Q11bVF7l2R}Mr"><field name="TEXT">T deg C</field></shadow><block type="variables_get" id="^Fz%}$S=7$I%LC:/e.eO"><field name="VAR" id="]|-(Rrj`E*/yCa~uoOG1">temperature</field></block></value><value name="VALUE2"><shadow type="math_number" id="2[-8g|lFD~7QDf64bm%Q"><field name="NUM">123</field></shadow><block type="text" id="TcHYD4V[+b[^WMnRSEAk"><field name="TEXT">C</field></block></value><next><block type="display_print2" id="Alu9k@{cr%Qv`-hk.D33"><value name="VALUE1"><shadow type="text" id="rx6mi)W?)f;9K315TuxP"><field name="TEXT">RH %</field></shadow><block type="variables_get" id="nJ-/y2|oS^@ntg#=0CC{"><field name="VAR" id=":il)3u?aiD*~+Aj;Ys^T">humidity</field></block></value><value name="VALUE2"><shadow type="math_number" id="N7/y,B]{8+WakrJo=n}E"><field name="NUM">123</field></shadow><block type="text" id="D67`pXCejGn5`ZsCOm]."><field name="TEXT">% Rel Humid</field></block></value><next><block type="display_print2" id="tUJbg9nG4O=(o`chr/K%"><value name="VALUE1"><shadow type="text" id="X[=]Qz.z~-iQd|/p]E-_"><field name="TEXT">Wind m/s</field></shadow><block type="str_format_float" id="fwz[Gl,|.0oI0b$2#rz4"><field name="D">2</field><field name="W">4</field><value name="VALUE"><block type="variables_get" id="0elJgFKbolX|Ll8Dzj@M"><field name="VAR" id="wgh23U+#tXJ{]nr3x^Pr">speed</field></block></value></block></value><value name="VALUE2"><shadow type="math_number" id="Ur(SPG2/o_9%WVNUr,d:"><field name="NUM">123</field></shadow><block type="text" id="#+nB5Jw9e:^Sz|#m5mg@"><field name="TEXT">m/s Wind</field></block></value><next><block type="variables_set" id="#l*SW(0eQWSWKfkA-Iqp"><field name="VAR" id="=AkE,RvMF/le:}G~I3.s">last_speed</field><value name="VALUE"><block type="variables_get" id="Xlnc!4f4L!-2R:[3jpB|"><field name="VAR" id="wgh23U+#tXJ{]nr3x^Pr">speed</field></block></value><next><block type="controls_if" id="K:SSV;.Qko2IoG=6?rnH"><value name="IF0"><block type="logic_compare" id="BraUb)NBuiUabP9Y|n7x"><field name="OP">EQ</field><value name="A"><block type="variables_get" id="$8ydY~!M8msGr@;]5t`B"><field name="VAR" id="wgh23U+#tXJ{]nr3x^Pr">speed</field></block></value><value name="B"><block type="variables_get" id="~H9K92@f*3]nSD=#]BfS"><field name="VAR" id="=AkE,RvMF/le:}G~I3.s">last_speed</field></block></value></block></value><statement name="DO0"><block type="variables_set" id="E3_)dZTlcQ!4jmzEy]gV"><field name="VAR" id="wgh23U+#tXJ{]nr3x^Pr">speed</field><value name="VALUE"><block type="math_number" id="?)%d-,7q|rVH+v]`d+!2"><field name="NUM">0</field></block></value></block></statement></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block><block type="event_every_loop" id="=wSo5}Y5A8S.=`PEuS4z" x="170" y="190"><statement name="DO"><block type="variables_set" id="pNZ.-Ka@QS8ZRpGk,R8y"><field name="VAR" id="5Td7r8uEJF$S)W=Tup;s">pulse_input</field><value name="VALUE"><block type="pin_in" id="i8YD,M(Dq!CFC[jq}u(*"><field name="PIN">P2</field></block></value><next><block type="controls_if" id="T6-G@#Y)+b=S[oH/rNMm"><mutation elseif="1"></mutation><value name="IF0"><block type="logic_operation" id="fL3V:(dC^h#jUnk:~^K."><field name="OP">AND</field><value name="A"><block type="variables_get" id="a[k_k(xWHXUjMC/GAkL1"><field name="VAR" id="5Td7r8uEJF$S)W=Tup;s">pulse_input</field></block></value><value name="B"><block type="logic_negate" id=")/#)xhK=i1T0]Pt5X$`H"><value name="BOOL"><block type="variables_get" id="-bacw+6XXSDvfpm@bG5c"><field name="VAR" id="0k=_|!W:y2]Y=D3XpjQ`">last_input</field></block></value></block></value></block></value><statement name="DO0"><block type="variables_set" id="xQE*v]6*nd@*-O,RHu$9"><field name="VAR" id="Gw!BPYM~_;Y_6FB0_ZEB">pulse_timer</field><value name="VALUE"><block type="time_time_ms" id="RL2:Mn;,j6ymy8Rpt~E?"></block></value><next><block type="variables_set" id="[BK1aat1m?8nC_sg_?4@"><field name="VAR" id="0k=_|!W:y2]Y=D3XpjQ`">last_input</field><value name="VALUE"><block type="logic_boolean" id="G*ZW,QxLr,*w%UFt2*o:"><field name="BOOL">TRUE</field></block></value><next><block type="led_on" id="Ryw(t}?Leq18u)=c6jP+"><field name="LED">led_orange</field></block></next></block></next></block></statement><value name="IF1"><block type="logic_operation" id="O.z]^}ti=~pCj,=gC8KS"><field name="OP">AND</field><value name="A"><block type="variables_get" id="QjtkdoK*6lGuK2/!.k6_"><field name="VAR" id="0k=_|!W:y2]Y=D3XpjQ`">last_input</field></block></value><value name="B"><block type="logic_negate" id="a~O%dR;D=Uy`{|]FPb|4"><value name="BOOL"><block type="variables_get" id="^xO3(x9pG6c]{pE-iKty"><field name="VAR" id="5Td7r8uEJF$S)W=Tup;s">pulse_input</field></block></value></block></value></block></value><statement name="DO1"><block type="variables_set" id="5Jb~*wi+$M_C#}()13G("><field name="VAR" id="0k=_|!W:y2]Y=D3XpjQ`">last_input</field><value name="VALUE"><block type="logic_boolean" id="`1pCkV@abC)[69l$f3-v"><field name="BOOL">FALSE</field></block></value><next><block type="variables_set" id="gY{~^1.fTt!jcEK|J8it"><field name="VAR" id="wgh23U+#tXJ{]nr3x^Pr">speed</field><value name="VALUE"><block type="math_arithmetic" id="omGuq$:1cn@g-`EPKNxR"><field name="OP">DIVIDE</field><value name="A"><shadow type="math_number" id="N2X=VYr4wujvc~=#kC$h"><field name="NUM">31</field></shadow></value><value name="B"><shadow type="math_number" id="}k6O(o.ZXCf#K_j4-q;$"><field name="NUM">1</field></shadow><block type="math_arithmetic" id="]uVBr)X!}yrYkO[b%+{U"><field name="OP">MINUS</field><value name="A"><shadow type="math_number" id="D,8PP`ROAQu[=4;[I{NW"><field name="NUM">1</field></shadow><block type="time_time_ms" id="`1$*D[I#::vFU~25wEjV"></block></value><value name="B"><shadow type="math_number" id="Z9t5oj%$Czw8Aen9e5m#"><field name="NUM">1</field></shadow><block type="variables_get" id="~fM]kAkZB!0qR,(0Q}-3"><field name="VAR" id="Gw!BPYM~_;Y_6FB0_ZEB">pulse_timer</field></block></value></block></value></block></value><next><block type="led_off" id="%r#}xM-f~M2UW.iutaug"><field name="LED">led_orange</field></block></next></block></next></block></statement></block></next></block></statement></block></xml>
