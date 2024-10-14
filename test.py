import torch
from torch import nn
import torchvision
from torchvision import datasets
from torchvision.transforms import ToTensor
import matplotlib
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from model import FashionMNISTModelV2
from tqdm import tqdm
import utils
matplotlib.use('Agg')


#print(f"Pytorch version:{torch.__version__}\n torchvision version:{torchvision.__version__}")

#load data
train_data=datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
    target_transform=None
)
test_data=datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor(),
    target_transform=None
)
class_names = train_data.classes
print(class_names)

#dataloader
BATCH_SIZE = 32
train_dataloader = DataLoader(train_data,
    batch_size = BATCH_SIZE,
    shuffle = True)
test_dataloader = DataLoader(test_data,
    batch_size = BATCH_SIZE,
    shuffle = False)

#CNN model
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
    #加入参数
torch.manual_seed(42)
model_2 = FashionMNISTModelV2(input_shape=1,
    hidden_units=10,
    output_shape=len(class_names)).to(device)
print(model_2)

#set loss and optimizer
import requests
from pathlib import Path

if Path("helper_functions.py").is_file():
    print("helper_functions.py已存在，跳过下载")
else:
    print("正在下载helper_functions.py")
    # 注意：你需要使用"raw" GitHub URL才能使其工作
    request = requests.get("https://raw.githubusercontent.com/mrdbourke/pytorch-deep-learning/main/helper_functions.py")
    with open("helper_functions.py", "wb") as f:
        f.write(request.content)


# 设置loss和optimizer
from helper_functions import accuracy_fn
from timeit import default_timer as timer

torch.manual_seed(42)
loss_fn = nn.CrossEntropyLoss() # this is also called "criterion"/"cost function" in some places
optimizer = torch.optim.SGD(params=model_2.parameters(), lr=0.1)
train_time_start_model_2 = timer()
epochs = 3
for epoch in tqdm(range(epochs)):
    print(f"Epoch: {epoch}\n---------")
    utils.train_step(data_loader=train_dataloader,
        model=model_2,
        loss_fn=loss_fn,
        optimizer=optimizer,
        accuracy_fn=accuracy_fn,
        device=device
    )
    utils.test_step(data_loader=test_dataloader,
        model=model_2,
        loss_fn=loss_fn,
        accuracy_fn=accuracy_fn,
        device=device
    )
train_time_end_model_2 = timer()
total_train_time_model_2 = utils.print_train_time(start=train_time_start_model_2,
                                           end=train_time_end_model_2,
                                           device=device)

#model eval and output
torch.manual_seed(42)
model_2_results = utils.eval_model(
    model=model_2,
    data_loader=test_dataloader,
    loss_fn=loss_fn,
    accuracy_fn=accuracy_fn
)
print(model_2_results)

