from snovault import upgrade_step


@upgrade_step('page', '', '2')
def page_0_2(value, system):
    # http://redmine.encodedcc.org/issues/4570

    allowedKeywords = [
        "3D chromatin structure",
        "DNA accessibility",
        "DNA binding",
        "DNA methylation",
        "Transcription",
        "RNA binding",
        "Genotyping",
        "Proteomics",
        "Conferences",
        "Encyclopedia",
    ]
    if 'news_keywords' in value:
        value['news_keywords'] = [kw for kw in value['news_keywords'] if kw in allowedKeywords]
