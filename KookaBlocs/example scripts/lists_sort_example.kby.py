import machine, kooka

list2 = None
i = None

def lists_sort(my_list, type, reverse):
    def try_float(s):
        try:
            return float(s)
        except:
            return 0
    key_funcs = {
        "NUMERIC": try_float,
        "TEXT": str,
        "IGNORE_CASE": lambda s: str(s).lower()
    }
    key_func = key_funcs[type]
    list_cpy = list(my_list)
    return sorted(list_cpy, key=key_func, reverse=reverse)


list2 = ['alpha', 'beta', 'gamma', 'delta']
for i in lists_sort(list2, "IGNORE_CASE", False):
    kooka.display.print(i, show=0)

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="b0D2eNTL,zd$_BU[hn)p">list</variable><variable id="U?s3C$u?%?}1Ln|ZGr*Z">i</variable></variables><block type="variables_set" id="[hq(#$%Jl31|qC`MTW_-" x="-210" y="-10"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field><value name="VALUE"><block type="lists_create_with" id="*}W@dSs2iH72[}-v0^(d"><mutation items="4"></mutation><value name="ADD0"><block type="text" id="GbHkjX;9DH;eH5CgV$[c"><field name="TEXT">alpha</field></block></value><value name="ADD1"><block type="text" id=",|_bIN*3^`To$5ASJjxl"><field name="TEXT">beta</field></block></value><value name="ADD2"><block type="text" id="}.-Cpf}!vt@?l2=kH@(}"><field name="TEXT">gamma</field></block></value><value name="ADD3"><block type="text" id="Hf}px}=LZ8Ie)RB}k|lR"><field name="TEXT">delta</field></block></value></block></value><next><block type="controls_forEach" id="x0R1{r[N3;*xeA)!ZOAj"><field name="VAR" id="U?s3C$u?%?}1Ln|ZGr*Z">i</field><value name="LIST"><block type="lists_sort" id="0m7|3d7/F?10ggZC!]YF"><field name="TYPE">IGNORE_CASE</field><field name="DIRECTION">1</field><value name="LIST"><block type="variables_get" id="[y!9mT}MM;H#+G)$qe|L"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value></block></value><statement name="DO"><block type="display_print" id="tj3y^DJy_KJ[I*s/qN,Q"><value name="VALUE"><shadow type="text" id="AVHaGWX0Da7Li?uOrd2p"><field name="TEXT">Hello</field></shadow><block type="variables_get" id="kkO|xFRQIt)D@RBev[-B"><field name="VAR" id="U?s3C$u?%?}1Ln|ZGr*Z">i</field></block></value></block></statement></block></next></block></xml>
