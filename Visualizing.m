clear all
clc
close all 
Csv = readtable('C:\Users\Admin\OneDrive - ai-quanton GmbH\LabLine Projekt\Code\MV\Measurements\Log.csv');

f1 = figure('Name', 'Means A, B, C, D');
x = Csv.XCoordinatesInMm;
y = Csv.YCoordinatesInMm;
v = Csv.MeansA;
[xq,yq] = meshgrid(min(x):.1:max(x), min(y):.1:max(y));
vq = griddata(x,y,v, xq, yq, 'cubic');
mesh(xq, yq, vq, 'FaceColor', 'b', 'EdgeColor', 'b', 'DisplayName','Channel A', 'FaceAlpha', 0.5, 'EdgeAlpha', 0.5)
hold on
x = Csv.XCoordinatesInMm;
y = Csv.YCoordinatesInMm;
v = Csv.MeansB;
[xq,yq] = meshgrid(min(x):.1:max(x), min(y):.1:max(y));
vq = griddata(x,y,v, xq, yq, 'cubic');
mesh(xq, yq, vq, 'FaceColor', 'r', 'EdgeColor', 'r', 'DisplayName','Channel B', 'FaceAlpha', 0.5, 'EdgeAlpha', 0.5)
hold on
x = Csv.XCoordinatesInMm;
y = Csv.YCoordinatesInMm;
v = Csv.MeansC;
[xq,yq] = meshgrid(min(x):.1:max(x), min(y):.1:max(y));
vq = griddata(x,y,v, xq, yq, 'cubic');
mesh(xq, yq, vq, 'FaceColor', '#77AC30', 'EdgeColor', '#77AC30', 'DisplayName','Channel C', 'FaceAlpha', 0.5, 'EdgeAlpha', 0.5)
hold on
x = Csv.XCoordinatesInMm;
y = Csv.YCoordinatesInMm;
v = Csv.MeansD;
[xq,yq] = meshgrid(min(x):.1:max(x), min(y):.1:max(y));
vq = griddata(x,y,v, xq, yq, 'cubic');
mesh(xq, yq, vq, 'FaceColor', '#EDB120', 'EdgeColor', '#EDB120', 'DisplayName','Channel D', 'FaceAlpha', 0.5, 'EdgeAlpha', 0.5)
xlabel('X Coordinates in mm');
ylabel('Y Coordinates in mm');
zlabel('Voltage in V');