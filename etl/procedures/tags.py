# -*- coding: utf-8 -*-

"""custom procedure to create tags column"""

import pandas as pd
import dask.dataframe as dd
from ddf_utils.chef.model.ingredient import ConceptIngredient
from ddf_utils.chef.helpers import debuggable
from ddf_utils.str import to_concept_id


def topic_to_tag(s):
    ls = s.replace('US$', 'USD').split(':')
    ls_ = [to_concept_id(x) for x in ls]
    return 'wdi__' + '__'.join(ls_)


@debuggable
def generate_tags(chef, ingredients, result):
    data = ingredients[0].get_data()
    new_data = dict()

    for k, df in data.items():
        df_ = df.copy()
        if 'topic' in df_.columns:
            df_['tags'] = df_['topic'].map(topic_to_tag)
        new_data[k] = df_

    return ConceptIngredient.from_procedure_result(result, ingredients[0].key, new_data)
