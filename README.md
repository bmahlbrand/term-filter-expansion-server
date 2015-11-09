# term-filter-expansion-server


<b>route:</b> host/expand_filter/[terms]  

Expected input for terms is term1&term2&term3&...&term  
returns JSON dictionary of arrays of expanded terms related (according to WordNet) to input  


use conf.ini to set host, port, and threshold for strength of relationships between terms
