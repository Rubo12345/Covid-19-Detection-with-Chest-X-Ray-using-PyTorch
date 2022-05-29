# Covid-19-Detection-with-Chest-X-Ray-using-PyTorch
Use Pytorch to create and train a ResNet-18 model and apply it to check X Ray Radiography Dataset to classify the X rays into three classes 'Normal', 'Viral Pneumonia', 'COVID'.

Dataset: Chest X-Ray Radiography Dataset[https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database]

1. Import Packages and Libraries (torch, torchvision, numpy, matplotlib, PIL, random)
2. Creating Custom Dataset - Pytorch Format 
3. Image Transformations (torchvision.transforms)
4. Prepare Dataloader (torch.utils.data.Dataloader)
5. Data Visualization - Plotting (Matplotlib)
6. Creating the Model (resnet18 - pretrained)
7. Training the Model (training the model until we get 95% accuracy)
8. Final Results (predictions)
