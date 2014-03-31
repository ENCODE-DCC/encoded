from ..migrator import upgrade_step


#@upgrade_step('biosample_characterization', '', '2')
def biosample_characterization_0_2(value, system):
    # http://redmine.encodedcc.org/issues/794
    if value.get('characterization_method') == "immunofluorescense":
        value['characterization_method'] = "immunofluorescence"
