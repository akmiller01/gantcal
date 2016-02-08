def uni(input):
    try:
        output = unicode(input).encode('latin1', 'replace')
    except:
        output = unicode(input).encode('utf-8', 'replace')
    return output