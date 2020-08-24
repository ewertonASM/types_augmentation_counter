import math
import statistics
import csv
import re
import os
import functools
import fire
from tqdm import tqdm
import pandas as pd
import copy


class Augmentation_Stats():

  validchars = "A-ZÁÉÍÓÚÀÂÊÔÃÕÜÇa-záéíóúàâêôãõüç"
  high_valid_chars = "[" + validchars + "]+"

  data = {
    'Famosos': {},
    'Ordinais': {},
    'Cardinais': {},
    'Romanos': {},
    'Lugares': {},
    'Direcionalidade': {},
    'Contexto': {},
    'Negacao': {},
    'Intensidade': {},
    'Sem_tipo': {}
  }

  separated_data = {
    'Famosos': [],
    'Ordinais': [],
    'Cardinais': [],
    'Romanos': [],
    'Lugares': [],
    'Direcionalidade': [],
    'Contexto': [],
    'Negacao': [],
    'Intensidade': [],
    'Sem_tipo': []
  }

  high_valid_chars_direcionality = "[" + validchars + '_' + "]+"

  old_patterns = {
    'Direcionalidade': "[1-3][SP]_"+high_valid_chars_direcionality+"_[1-3][SP]",
    'Intensidade': '\([+-]\)'+high_valid_chars,
    'Negacao': 'NÃO_'+high_valid_chars,
    'Famosos': high_valid_chars+'[_&]FAMOS[AO]',
    'Lugares': high_valid_chars+'[_&](PAÍS|ESTADO|CIDADE)',
    'Romanos': '^(?=[MDCLXVI])M*(C[MD]|D?C*)(X[CL]|L?X*)(I[XV]|V?I*)$',
    'Ordinais': '[1-9][ºª]',
    'Cardinais': '[0-9](?![SPºª0-9])',
    'Contexto': '(?<!NÃO)(?<![1-3][SP])[_|&](?!\w*PAÍS|\w*ESTADO|\w*CIDADE|\w*[1-3][SP]|\w*[&|_]*FAMOSO)'
  }

  patterns = {
    'Direcionalidade': high_valid_chars_direcionality+'_[1-3][SP]_[1-3][SP]',
    'Intensidade': high_valid_chars+'\([+-]\)',
    'Negacao': 'NÃO_'+high_valid_chars,
    'Famosos': high_valid_chars+'&FAMOS[AO]',
    'Lugares': high_valid_chars+'&(PAÍS|ESTADO|CIDADE)',
    'Romanos': '^(?=[MDCLXVI])M*(C[MD]|D?C*)(X[CL]|L?X*)(I[XV]|V?I*)$',
    'Ordinais': '[1-9][ºª]',
    'Cardinais': '[0-9](?![SPºª0-9])',
    'Contexto': '(?<!NÃO)(?<![1-3][SP])[_|&](?!\w*PAÍS|\w*ESTADO|\w*CIDADE|\w*[1-3][SP]|\w*[&|_]*FAMOSO)'
  }

  

  def __init__(self, file, output_file):
    self.file = file
    self.output_file = output_file
    self.f = open(output_file, 'w')

  def file_init(self):

    with open(self.file,  encoding="utf-8-sig") as f:
      corpus = [(pt,gi) for pt,gi in csv.reader(f)]
      
    return corpus

  def maintenance_by_case(self, word, augmentation):


    updated_word = word
    
    if augmentation == 'Direcionalidade':


      fragmented_directional = re.split('_(?=[1-3][SP])|(?<=[1-3][SP])_', word)
      recombined_directional = f'{fragmented_directional[1]}_{fragmented_directional[0]}_{fragmented_directional[2]}'
      # updated_gi = updated_gi.replace(word, recombined_directional)
      updated_word = recombined_directional

    elif augmentation == 'Intensidade':

      fragmented_intensity = re.split('(?<=\))', word)
      recombined_intensity = f'{fragmented_intensity[1]}{fragmented_intensity[0]}'
      # updated_gi = updated_gi.replace(word, recombined_intensity)
      updated_word = recombined_intensity

    elif augmentation == 'Famosos':


      updated_word = re.sub('_(?=FAMOS[AO])', '&', word)
      # updated_gi = updated_gi.replace(word, updated_word)

    elif augmentation == 'Lugares':

      updated_word = re.sub('_(?=PAÍS|ESTADO|CIDADE)', '&', word)
      # updated_gi = updated_gi.replace(word, updated_word)

    elif augmentation == 'Contexto':

      updated_word = re.sub('_(?=[^_]*$)', '&', word)
      # updated_gi = updated_gi.replace(word, updated_word)


    
    return (word,updated_word)
    

  def update_pattern(self, corpus):

    updated_pattern_data = []

    updated_gi = ''
    
    for pt, gi in tqdm(corpus):


      
      updated_gi = gi
      words_tuples = []

      for augmentation, pattern in self.old_patterns.items():

        # splitted_gi = copy.deepcopy(updated_gi.split()) 
        for word in updated_gi.split():

          # print(word)

          if re.search(pattern, word):
            # if word.startswith("REINO"):
            #   print(updated_gi)
            #   print(word)
            #   print(augmentation)
            
            words_tuples.append(self.maintenance_by_case(word, augmentation))
            # print('pattern:',augmentation,word,':', updated_word)

      for word, updated_word in words_tuples:
        updated_gi = updated_gi.replace(word,updated_word)
      updated_pattern_data.append((pt,updated_gi))

    return updated_pattern_data




  def get_augmentation_stats(self):

    corpus = self.file_init()
    # corpus = self.update_pattern(corpus)

    corpus.sort()
    # print(corpus)

    # corpus_df = pd.DataFrame(corpus)

  

    # corpus_df.to_csv(
    #     f"./output/romans_splitted.csv",
    #     header=None,
    #     encoding="utf-8-sig",
    #     index=False,
    # )


    # exit()
    mutiples_cases = {}
    romans_clear_pattern = '[^A-ZÁÉÍÓÚÀÂÊÔÃÕÜÇa-záéíóúàâêôãõüç°]+'

    for index, (pt,gi) in enumerate(corpus):

      no_aug = False
      cases_counter = 0
      cases_list = []
      one_case_aug = False

      for index_pattern, (augmentation, pattern) in enumerate(self.patterns.items()):

        augmentation_occurrences = []

        for word in gi.split():

          if augmentation == 'Romanos':
            word = re.sub(romans_clear_pattern,'',word)

          if re.search(pattern, word):
            augmentation_occurrences.append(word)

        if augmentation_occurrences:
          no_aug = True
          cases_counter += 1
          founded_aug = augmentation
          cases_list.append(augmentation)
          self.data[augmentation][index+1] = len(augmentation_occurrences)

        if index_pattern == len(self.patterns)-1:
          if cases_counter == 1:
            one_case_aug = founded_aug

        

      if cases_counter > 1:
        key = ', '.join(cases_list)

        if key in mutiples_cases:
          mutiples_cases[key].append(index+1)
        else:
          if key:
            mutiples_cases[key] = [index+1]
        key = False
      elif one_case_aug:
        self.separated_data[one_case_aug].append((pt,gi))
      else:
        self.separated_data['Sem_tipo'].append((pt,gi))

      if not no_aug:
        self.data['Sem_tipo'][index+1] = 1

    total_phrases = self.statistics_generator()

    print("* Multiplos casos:\n")

    multiples_cases_lenght = 0
    
    for key, value in mutiples_cases.items():
      multiples_cases_lenght = multiples_cases_lenght + len(value)
      print(f'  - {key}: {len(value)}')

    print(f'Total de frases: {len(total_phrases)}')

    self.generate_csv()

  def statistics_generator(self):

    total_phrases = []

    for key, value in self.data.items():

      absolut_occurrences = 0
      phrases_with_cases = 0
      phrases_with_cases = len(value)


      for sub_key, sub_value in value.items():
            absolut_occurrences = absolut_occurrences + sub_value
            total_phrases.append(sub_key)

      print(f'number of occurrences  - {key}: {absolut_occurrences}')
      print(f'phrases with cases - {key}: {phrases_with_cases}\n')

    print("\n\n\n")

    return set(total_phrases)



  def generate_csv(self):

    for augs in self.separated_data:
      list_phrases_df = pd.DataFrame(self.separated_data[augs])

      list_phrases_df.to_csv(
          f"./output/{augs}.csv",
          header=None,
          encoding="utf-8-sig",
          index=False,
      )

if __name__ == "__main__":

  test_corpus = '/home/ewerton/Workspace/Vlibras/augmentation_count/input/splitted_romans.csv'

  output_file = 'output/v5/overfitting_augmentation_analysis.txt'

  augmentationStats = Augmentation_Stats(file=test_corpus, \
                              output_file=output_file)

  augmentationStats.get_augmentation_stats()
