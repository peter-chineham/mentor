
def get_nodes():
    nodes = []
    profile = open('ip_list', 'r')
    for inar in profile:
        inar = inar[:len(inar)-1]
        nodes.append(inar)
    return (nodes)
