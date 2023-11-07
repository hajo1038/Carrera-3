% Create a UDP socket
udp_ip = '192.168.1.2';
udp_port = 4210;
global udp_socket
udp_socket = udpport('byte', 'LocalHost', udp_ip, 'LocalPort', udp_port, 'ByteOrder', 'big-endian');
%configureCallback(udp_socket,"byte", 24, @update_plots);
tic;
%udp_socket = 10;
%fopen(udp_socket);

% Create a figure with 6 subplots for real-time plotting
h = figure('Position', [100, 100, 800, 600]);
subplot(3, 2, 1);
plot(0, 0, 'r-');
title('Beschleunigung in x');
axis([0 100 -100 100]);
%xlim auto
ylim auto

subplot(3, 2, 3);
plot(0, 0, 'g-');
title('Beschleunigung in y');
axis([0 100 -100 100]);
ylim auto

subplot(3, 2, 5);
plot(0, 0, 'b-');
title('Beschleunigung in z');
axis([0 100 -100 100]);
ylim auto

subplot(3, 2, 2);
plot(0, 0, 'r-');
title('Drehrate in x');
axis([0 100 -100 100]);
ylim auto

subplot(3, 2, 4);
plot(0, 0, 'g-');
title('Drehrate in y');
axis([0 100 -100 100]);
ylim auto

subplot(3, 2, 6);
plot(0, 0, 'b-');
title('Drehrate in z');
axis([0 100 -100 100]);
ylim auto

% Set up a timer for updating plots
update_interval = 0.05; % Update every 50 milliseconds
t = timer('ExecutionMode', 'fixedRate', 'Period', update_interval);
t.TimerFcn = {@update_plots, udp_socket};
start(t);


% Set up cleanup function to execute when the figure is closed
set(gcf, 'CloseRequestFcn', {@cleanup, t});

% Keep the figure open
uiwait(gcf);

function update_plots(~, ~, socket)
%function update_plots(socket,~)
    data = read(socket, 6, 'int32'); % Read 24 bytes as 6 int32 values
    %video_data = read(socket, socket.NumBytesAvailable);
    video_data = readline(socket);
    res = matlab.net.base64decode(video_data)
    %video_data_uint8 = uint8(video_data);
    %video_data_bin = dec2bin(video_data_uint8);
    img_height = 240;
    img_width = 320;
    flush(socket);
    sensor_data = data';
    f = gcf;
    for i = 1:6
        j = 7-i; %Children order is reversed, therefore use j for children
        f.Children(j).Children.YData = [f.Children(j).Children.YData sensor_data(i)];
        f.Children(j).Children.XData = [f.Children(j).Children.XData toc];
        %f.Children(i).YLim = [min(f.Children(i).Children.YData(end-10)), max(f.Children(i).Children.YData(end))];
        f.Children(j).XLim = [toc-5, toc+5];
    end
    % Update plot limits if needed
    %xlim([max(0, numel(get(plot_data1, 'YData')) - 100), numel(get(plot_data1, 'YData'))]);
    %ylim([-100 100]);
end

% Create a function to clean up and close the UDP connection when done
function cleanup(~, ~, timer_t)
    clear global udp_socket;
    f = gcf;
    stop(timer_t);
    delete(timer_t);
    clear timer_t;
    delete(gcf); % Close the figure
    i = 0;
    while isfile(sprintf("Carrera_Daten_%u.mat",i))
        i = i+1;
    end
    filename = sprintf("Carrera_Daten_%u.mat",i);
    save(filename, 'f')
end