# -*- coding: utf-8 -*-
"""help.ipynb의 사본

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1izDGj667PoIEPG9McAK9NcNmmA4Byucr

### **스크립트 내 포함해야하는 함수**
  - set_device()
  - custom_collate_fn()
"""

def set_device(torch):

  # device type
  if torch.cuda.is_available():
      device = torch.device("cuda")
      print(f"# available GPUs : {torch.cuda.device_count()}")
      print(f"GPU name : {torch.cuda.get_device_name()}")

  else:
      device = torch.device("cpu")

  return device

import torch
from transformers import BertTokenizer
tokenizer_bert = BertTokenizer.from_pretrained("klue/bert-base")

def custom_collate_fn(batch):
  """
  - batch: list of tuples (input_data(string), target_data(int))
  
  한 배치 내 문장들을 tokenizing 한 후 텐서로 변환함. 
  이때, dynamic padding (즉, 같은 배치 내 토큰의 개수가 동일할 수 있도록, 부족한 문장에 [PAD] 토큰을 추가하는 작업)을 적용
  토큰 개수는 배치 내 가장 긴 문장으로 해야함.(padding = 'longest')
  또한 최대 길이를 넘는 문장은 최대 길이 이후의 토큰을 제거하도록 해야 함 (truncation=True)
  토크나이즈된 결과 값은 텐서 형태로 반환하도록 해야 함 (return_tensors = 'pt')
  
  한 배치 내 레이블(target)은 텐서화 함.
  
  (input, target) 튜플 형태를 반환.
  """
  global tokenizer_bert

  input_list, target_list = [], []
  
  for text, label in batch:
    target_list.append(label)
    input_list.append(text)
  


  tensorized_input = tokenizer_bert(input_list, 
                                    padding=True, 
                                    truncation=True, 
                                    return_tensors='pt')
  
  tensorized_label = torch.tensor(target_list)
  
  return tensorized_input, tensorized_label

"""
### **포함해야하는 클래스**
- CustomDataset
- CustomClassifier"""

from torch.utils.data import Dataset

class CustomDataset(Dataset): # torch.utils.data.Dataset()
  """
  - input_data: list of string
  - target_data: list of int
  """

  def __init__(self, input_data:list, target_data:list):
      self.X = input_data
      self.Y = target_data


  def __len__(self):
      return len(self.Y)

  def __getitem__(self, index):
    input = self.X[index]
    label = self.Y[index]

    return input, label

import torch.nn as nn
from transformers import BertModel

class CustomClassifier(nn.Module):

  def __init__(self, hidden_size: int, n_label: int):
    super(CustomClassifier, self).__init__()

    self.bert = BertModel.from_pretrained("klue/bert-base")

    dropout_rate = 0.1
    linear_layer_hidden_size = 32

    self.classifier = nn.Sequential(
                        nn.Linear(hidden_size, linear_layer_hidden_size),
                        nn.ReLU(),
                        nn.Dropout(dropout_rate),
                        nn.Linear(linear_layer_hidden_size, n_label)
    ) # torch.nn에서 제공되는 Sequential, Linear, ReLU, Dropout 함수 활용

  def forward(self, input_ids=None, attention_mask=None, token_type_ids=None):
    outputs = self.bert(
        input_ids,
        attention_mask=attention_mask,
        token_type_ids=token_type_ids,
    )

    # BERT 모델의 마지막 레이어의 첫번재 토큰을 인덱싱
    cls_token_last_hidden_states = outputs['pooler_output'] # pooler_output : 마지막 layer의 첫 번째 토큰 ("[CLS]") 벡터, shape = (1, hidden_size)
    logits = self.classifier(cls_token_last_hidden_states)

    return logits