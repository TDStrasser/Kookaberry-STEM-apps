import machine, kooka

def math_modes(some_list):
    modes = []
    # Using a lists of [item, count] to keep count rather than dict
    # to avoid "unhashable" errors when the counted item is itself a list or dict.
    counts = []
    maxCount = 1
    for item in some_list:
        found = False
        for count in counts:
            if count[0] == item:
                count[1] += 1
                maxCount = max(maxCount, count[1])
                found = True
        if not found:
            counts.append([item, 1])
    for counted_item, item_count in counts:
        if item_count == maxCount:
            modes.append(counted_item)
    return modes


kooka.display.print(math_modes([-123, 123, 123, -123]), show=0)

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="display_print" id="j4o(tI,zR]_YKS{6^=/}" x="-190" y="-230"><value name="VALUE"><shadow type="text" id="~4]W%SMAJHpJexFAR0#U"><field name="TEXT">Hello</field></shadow><block type="math_on_list" id="]e;;a{LfbDH(bU*6*}T}"><mutation op="MODE"></mutation><field name="OP">MODE</field><value name="LIST"><block type="lists_create_with" id="!A%8Vl+XR;Y0m_mbhhTD"><mutation items="4"></mutation><value name="ADD0"><block type="math_number" id="jWLhoU5e)UAo$fU6:|-8"><field name="NUM">-123</field></block></value><value name="ADD1"><block type="math_number" id="^FQn.po$nTDffedssQ+}"><field name="NUM">123</field></block></value><value name="ADD2"><block type="math_number" id="HV..GE3D-L8HHZVl{MZ9"><field name="NUM">123</field></block></value><value name="ADD3"><block type="math_number" id="o)7g#MPkuWm224K%o=Q#"><field name="NUM">-123</field></block></value></block></value></block></value></block></xml>
