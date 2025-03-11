clear
clc
close all

neff1 = 2.545144;   % From Sim
neff2 = 3.1;        % From Rushabh

ff = 0.5;
neff_avg = ff*neff1 + (1-ff)*neff2;

lambda_0 = 1550;
lambda = lambda_0 / neff_avg;

theta_air = (-pi/4):0.01:(pi/4);   % 90 degrees

gratingPeriod = lambda_0 ./ (neff_avg - sin(theta_air));

plot(theta_air, gratingPeriod)





