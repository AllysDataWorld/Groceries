# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 07:37:05 2024

@author: after
"""

def levenshtein_distance(str1, str2):
    if len(str1) < len(str2):
        return levenshtein_distance(str2, str1)

    if len(str2) == 0:
        return len(str1)

    previous_row = range(len(str2) + 1)
    for i, c1 in enumerate(str1):
        current_row = [i + 1]
        for j, c2 in enumerate(str2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


# str1 = "kitten"
# str2 = "sitting"
#distance = levenshtein_distance(str1, str2)
#print(f"The Levenshtein Distance between '{str1}' and '{str2}' is {distance}.")





