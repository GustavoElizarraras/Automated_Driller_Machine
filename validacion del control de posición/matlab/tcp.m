clc
clear all 

pulsosx=0;
pulsosy=0;
pulsospx=0;
pulsospy=0;
ctrx=0;
ctry=0;
px=[];
py=[];
tmp=[];
xc=0;
recordx=[];
recordy=[];

delete(instrfind({'port'},{'COM7'}));
puerto=serialport('COM7',9600);
puerto.BaudRate=9600;
fopen(puerto);
t=10;
tic

while toc<t
    pulsospx=pulsosx;
    pulsosx=fscanf(puerto,'%f');
    recordx=[recordx pulsosx];
    pulsospy=pulsosy;
    recordy=[recordy pulsosy];
    pulsosy=fscanf(puerto,'%f');
    if pulsospx==0 & pulsosx==1
        ctrx=ctrx+1;
    end
     if pulsospy==0 & pulsosy==1
         ctry=ctry+1;
     end
     px=[px ctrx];
     py=[py ctry];
     xc=xc+1;
     tmp=[tmp xc];
    ctrx
    ctry
end

subplot(2,1,1)
plot(recordx)
subplot(2,1,2)
plot(recordy)

% px=px*0.02;
% py=py*0.02;
% tmp=tmp/5120;
% figure
% plot(tmp,px,'r','LineWidth',1.5)
% hold on
% plot(tmp,py,'--g','LineWidth',1.5)
% grid on
% grid minor
% xlabel('t [s]')
% ylabel('[mm]')
% legend('eje x',' eje y')
% title('posición - tiempo')

% vx=([px 0]-[0 px])./([tmp 0]-[0 tmp])/3;
% vy=([py 0]-[0 py])./([tmp 0]-[0 tmp])/3;
% figure
% subplot(2,1,1)
% plot([0 tmp],vx,'--r')
% grid on
% grid minor
% xlabel('t [s]')
% ylabel('[mm/s]')
% title('velocidad - tiempo (eje x)')
% subplot(2,1,2)
% plot([0 tmp],vy,'--g')
% grid on
% grid minor
% xlabel('t [s]')
% ylabel('[mm/s]')
% title('velocidad - tiempo (eje y)')

% %Comunicacion con unity
% tcpipCliente = tcpclient('127.0.0.1',55000);
% fopen(tcpipCliente);
% fwrite(tcpipCliente,ctrx);
% fwrite(tcpipCliente,ctry);
% fclose(tcpipCliente);




  
