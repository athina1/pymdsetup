"""Mutation fetcher module

"""
import requests
import re


class MmbVariants(object):
    """
    """

    def __init__(self, pdb_code):
        self.pdb_code = pdb_code.lower()
        self.uniprot = self.get_uniprot()

    def get_uniprot(self):
        url_uniprot_id = ("http://mmb.irbbarcelona.org"
                          "/api/pdb/"+self.pdb_code.lower()+"/entry"
                          "/uniprotRefs/_id")
        return requests.get(url_uniprot_id).json()['uniprotRefs._id'][0]

    def get_variants(self):
        url_uniprot_mut = ("http://mmb.irbbarcelona.org"
                           "/api/uniprot/"+self.uniprot+"/entry"
                           "/variants/vardata/mut/")
        return requests.get(url_uniprot_mut).json()['variants.vardata.mut']

    def get_pdb_variants(self):
        url_mapPDBRes = ("http://mmb.irbbarcelona.org/api/"
                         "uniprot/"+self.uniprot+"/mapPDBRes")

        pattern = re.compile(("p.(?P<wt>[a-zA-Z]{3})"
                              "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))

        unfiltered_dic = requests.get(url_mapPDBRes).json()
        mapdic = {}
        mutations = []
        for k in unfiltered_dic.keys():
            if k.startswith(self.pdb_code.upper()):
                mapdic[k[-1]] = unfiltered_dic[k]
        uniprot_var = self.get_variants()
        for var in uniprot_var:
            uni_mut = pattern.match(var).groupdict()
            for k in mapdic.keys():
                for fragment in mapdic[k]:
                    unp_s = int(fragment['unp_start'])
                    uni_mut_resnum = int(uni_mut['resnum'])
                    unp_e = int(fragment['unp_end'])
                    pdb_s = int(fragment['pdb_start'])
                    if unp_s <= uni_mut_resnum <= unp_e:
                        resnum = uni_mut_resnum + pdb_s - unp_s
                        mutations.append(k + '.' + uni_mut['wt'] +
                                         str(resnum) + uni_mut['mt'])
        return mutations
