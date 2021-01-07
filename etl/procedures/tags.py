# -*- coding: utf-8 -*-

"""custom procedure to create tags column"""

import logging
import pandas as pd
import dask.dataframe as dd
from ddf_utils.chef.model.ingredient import ConceptIngredient, EntityIngredient
from ddf_utils.chef.helpers import debuggable
from ddf_utils.str import to_concept_id


logger = logging.getLogger('tags')


def topic_to_tag(s):
    if pd.isnull(s):
        return 'wdi__uncategorized'
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
            if df_['topic'].hasnans:
                logger.warning("there are concepts without any topic:")
                logger.warning(df_[pd.isnull(df_['topic'])]['concept'].values)
            df_['tags'] = df_['topic'].map(topic_to_tag)
        # fill missing tags with "wdi"
        df_['tags'] = df_['tags'].fillna('wdi')
        new_data[k] = df_

    return ConceptIngredient.from_procedure_result(result, ingredients[0].key, new_data)


@debuggable
def update_tag_entity(chef, ingredients, concept_ingredient, result):
    data =  ingredients[0].get_data()
    tags_df = data['tag'].copy()

    concept_df = chef.dag.get_node(concept_ingredient).evaluate().get_data()['concept']

    concept_tags = concept_df[['tags', 'topic']].drop_duplicates()
    concept_tags.columns = ['tag', 'name']
    concept_tags['parent'] = None

    missing = list()
    for tag in concept_tags['tag'].values:
        if tag not in tags_df['tag'].values:
            missing.append(tag)
    if len(missing) > 0:
        tags_df = tags_df.append(concept_tags[concept_tags['tag'].isin(missing)], ignore_index=True)

    new_data = {'tag': tags_df}
    return EntityIngredient.from_procedure_result(result, ingredients[0].key, new_data)
