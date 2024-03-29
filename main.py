import torch
import numpy as np
import os
import shutil
import random
import torchvision
from PIL import Image
from matplotlib import pyplot as plt
import sys
import pandas as pd

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
sys.path.append('/home/rutu/Guided_Projects/Covid-19-Detection-with-Chest-X-Ray-using-PyTorch/archive/')

torch.manual_seed(0)
# print('Using Pytorch version',torch.__version__)

class_names = ['normal', 'viral', 'covid']
root_dir = 'COVID-19_Radiography_Database'
source_dirs = ['Normal', 'Viral Pneumonia', 'COVID']

if os.path.isdir(os.path.join(root_dir, source_dirs[1])):
    os.mkdir(os.path.join(root_dir, 'test'))

    for i, d in enumerate(source_dirs):
        os.rename(os.path.join(root_dir, d), os.path.join(root_dir, class_names[i]))

    for c in class_names:
        os.mkdir(os.path.join(root_dir, 'test', c))

    for c in class_names:
        images = [x for x in os.listdir(os.path.join(root_dir, c)) if x.lower().endswith('png')]
        selected_images = random.sample(images, 30)
        for image in selected_images:
            source_path = os.path.join(root_dir, c, image)
            target_path = os.path.join(root_dir, 'test', c, image)
            shutil.move(source_path, target_path)

class ChestXRayDataset(torch.utils.data.Dataset):
    def __init__(self, image_dirs, transform):
        def get_images(class_name):
            # print(os.listdir(image_dirs[class_name]))
            images = [x for x in os.listdir(image_dirs[class_name]) if x[-3:].lower().endswith('png')]
            # print(f'Found {len(images)} {class_name} examples')
            # print(images)
            return images
        
        self.images = {}
        self.class_names = ['normal', 'viral', 'covid']
        
        for class_name in self.class_names:
            self.images[class_name] = get_images(class_name)
            
        self.image_dirs = image_dirs
        self.transform = transform
        
    def __len__(self):
        return sum([len(self.images[class_name]) for class_name in self.class_names])
    
    def __getitem__(self, index):
        class_name = random.choice(self.class_names)
        index = index % len(self.images[class_name])
        image_name = self.images[class_name][index]
        image_path = os.path.join(self.image_dirs[class_name], image_name)
        image = Image.open(image_path).convert('RGB')
        return self.transform(image), self.class_names.index(class_name)
        
train_transform = torchvision.transforms.Compose([
    torchvision.transforms.Resize(size=(224, 224)),
    torchvision.transforms.RandomHorizontalFlip(),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

test_transform = torchvision.transforms.Compose([
    torchvision.transforms.Resize(size=(224, 224)),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

train_dirs = {
    'normal': 'archive/COVID-19_Radiography_Database/normal/images/',
    'viral': 'archive/COVID-19_Radiography_Database/viral/images/',
    'covid': 'archive/COVID-19_Radiography_Database/covid/images/'
}
train_dataset = ChestXRayDataset(train_dirs, train_transform)

test_dirs = {
    'normal': 'archive/COVID-19_Radiography_Database/test/normal/',
    'viral': 'archive/COVID-19_Radiography_Database/test/viral/',
    'covid': 'archive/COVID-19_Radiography_Database/test/covid/'
}
test_dataset = ChestXRayDataset(test_dirs, test_transform)

batch_size = 28
dl_train = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
dl_test = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

# print('Number of training batches', len(dl_train))
# print('Number of test batches', len(dl_test))

class_names = train_dataset.class_names
def show_images(images, labels, preds):
    plt.figure(figsize=(8, 4))
    for i, image in enumerate(images):
        plt.subplot(1, 6, i + 1, xticks=[], yticks=[])
        image = image.numpy().transpose((1, 2, 0))
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = image * std + mean
        image = np.clip(image, 0., 1.)
        plt.imshow(image)
        col = 'green'
        if preds[i] != labels[i]:
            col = 'red'
        plt.xlabel(f'{class_names[int(labels[i].numpy())]}')
        plt.ylabel(f'{class_names[int(preds[i].numpy())]}', color=col)
    plt.tight_layout()
    plt.show()

images, labels = next(iter(dl_train))
# show_images(images, labels, labels)

images, labels = next(iter(dl_test))
# show_images(images, labels, labels)

resnet18 = torchvision.models.resnet18(pretrained=False)   #With/Without pretrained weights
resnet18.fc = torch.nn.Linear(in_features=512, out_features=3)
resnet18.to(device)
loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(resnet18.parameters(), lr=3e-5)

def show_preds():
    resnet18.eval()
    images, labels = next(iter(dl_test))
    print(images.shape)
    outputs = resnet18(images)
    print(outputs.shape)
    _, preds = torch.max(outputs, 1)
    show_images(images, labels, preds)
# show_preds()

def train(epochs):
    print('Starting training..')
    Valid_Loss = []
    Train_Loss = []
    Accuracy = []
    VL = "Validation Loss"
    ACC = "Accuracy"
    TL = "Train Loss"
    for e in range(0, epochs):
        print('='*20)
        print(f'Starting epoch {e + 1}/{epochs}')
        print('='*20)
    
        train_loss = 0.
        val_loss = 0.

        resnet18.train() # set model to training phase

        for train_step, (images, labels) in enumerate(dl_train):
            optimizer.zero_grad()
            image = images.to(device)
            label = labels.to(device)
            outputs = resnet18(image)
            loss = loss_fn(outputs, label)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            if train_step % 20 == 0:
                print('Evaluating at step', train_step)
                accuracy = 0
                correct = 0
                resnet18.eval() # set model to eval phase

                for val_step, (images, labels) in enumerate(dl_test):
                    image = images.to(device)
                    label = labels.to(device)
                    outputs = resnet18(image)
                    loss = loss_fn(outputs, label)
                    val_loss += loss.item()

                    _, preds = torch.max(outputs, 1)
                    correct += (preds == label).sum().item()
                accuracy = 100 * correct / len(test_dataset)
                val_loss /= (val_step + 1)
                # accuracy = accuracy/len(test_dataset)
                # accuracy = 100*accuracy
                Accuracy.append(accuracy)
                Valid_Loss.append(val_loss)

                print(f'Epoch: {e+1},Validation Loss: {val_loss:.4f}, Accuracy: {accuracy:.4f}')

                # show_preds()

                resnet18.train()

                # if accuracy >= 0.95:
                #     print('Performance condition satisfied, stopping..')
                #     return

        train_loss /= (train_step + 1)
        Train_Loss.append(train_loss)
        print(f'Training Loss: {train_loss:.4f}')
    print('Training complete..')
    data = pd.DataFrame({VL:Valid_Loss,ACC:Accuracy})
    data.to_excel('Loss_and_Acc.xlsx',sheet_name = 'Losses and Accuracy', index = True)
    data2 = pd.DataFrame({TL : Train_Loss})
    data2.to_excel('Tr_Loss.xlsx',sheet_name = 'Train Loss', index = True)

train(epochs=10)
# show_preds()