% 0. AUTO-LOAD THE FRESHEST DATA
thesis_data = readtable('thesis_data.csv');

% 1. CREATE THE INTERACTIVE POP-UP MENU
% First, build the list of options using the IDs and Dates from the CSV
menu_options = cell(height(thesis_data) + 1, 1);
menu_options{1} = '🌟 LATEST RUN (Auto-select newest)';
for i = 1:height(thesis_data)
    menu_options{i+1} = sprintf('Run ID: %d  |  Date: %s', thesis_data.run_id(i), string(thesis_data.date(i)));
end

% Second, show the clickable menu box to the user
[selection, is_valid] = listdlg('PromptString', 'Select a Maze Run to Analyze:', ...
                                'SelectionMode', 'single', ...
                                'Name', 'Database Selector', ...
                                'ListSize', [350, 200], ...
                                'ListString', menu_options);

% If the user clicks "Cancel" or closes the window, stop the script safely
if is_valid == 0
    disp('Analysis cancelled by user.');
    return;
end

% Third, figure out which row they selected
if selection == 1
    run_idx = height(thesis_data); % They clicked the 'Latest Run' star
else
    run_idx = selection - 1;       % They clicked a specific historical run
end

run_id_name = num2str(thesis_data.run_id(run_idx));

% ---------------------------------------------------------
% (Leave Step 2 and beyond exactly as it was!)
% 2. Extract the Path lengths
bfs_path = thesis_data.bfs_path(run_idx);
dfs_path = thesis_data.dfs_path(run_idx);

% 2. Extract the 4 metrics for just this ONE specific maze
bfs_p = thesis_data.bfs_path(run_idx);     dfs_p = thesis_data.dfs_path(run_idx);
bfs_t = thesis_data.bfs_time_ms(run_idx);  dfs_t = thesis_data.dfs_time_ms(run_idx);
bfs_n = thesis_data.bfs_nodes(run_idx);    dfs_n = thesis_data.dfs_nodes(run_idx);
bfs_m = thesis_data.bfs_mem_kb(run_idx);   dfs_m = thesis_data.dfs_mem_kb(run_idx);

path_data = [bfs_p, dfs_p];
time_data = [bfs_t, dfs_t];
node_data = [bfs_n, dfs_n];
mem_data  = [bfs_m, dfs_m];

% 3. CALCULATE OVERALL EFFICIENCY (Normalizing all 4 metrics)
% The winner of each category gets 100%, the loser gets a fraction
bfs_score = mean([ (min(path_data)/bfs_p)*100, (min(time_data)/bfs_t)*100, (min(node_data)/bfs_n)*100, (min(mem_data)/bfs_m)*100 ]);
dfs_score = mean([ (min(path_data)/dfs_p)*100, (min(time_data)/dfs_t)*100, (min(node_data)/dfs_n)*100, (min(mem_data)/dfs_m)*100 ]);

fprintf('\n---> OVERALL EFFICIENCY: BFS = %.2f%% | DFS = %.2f%% <---\n', bfs_score, dfs_score);

% 4. Set up the 2x2 Comparative Dashboard Figure
figure('Name', 'Single Maze Comparison', 'Position', [100, 100, 800, 600]);
algos = categorical({'BFS', 'DFS'});

% --- TOP LEFT: Path Length ---
subplot(2,2,1);
b1 = bar(algos, path_data, 'FaceColor', [0.2 0.6 0.8]); % Blue
title('Path Length (Optimality)'); ylabel('Total Steps'); grid on;
text(b1.XEndPoints, b1.YEndPoints, string(path_data), 'HorizontalAlignment','center', 'VerticalAlignment','bottom', 'FontWeight', 'bold');

% --- TOP RIGHT: Execution Time ---
subplot(2,2,2);
b2 = bar(algos, time_data, 'FaceColor', [0.8 0.4 0.2]); % Orange
title('Execution Time (Speed)'); ylabel('Milliseconds (ms)'); grid on;
text(b2.XEndPoints, b2.YEndPoints, string(time_data), 'HorizontalAlignment','center', 'VerticalAlignment','bottom', 'FontWeight', 'bold');

% --- BOTTOM LEFT: Nodes Explored ---
subplot(2,2,3);
b3 = bar(algos, node_data, 'FaceColor', [0.17 0.74 0.51]); % Green
title('Nodes Explored (Efficiency)'); ylabel('Node Count'); grid on;
text(b3.XEndPoints, b3.YEndPoints, string(node_data), 'HorizontalAlignment','center', 'VerticalAlignment','bottom', 'FontWeight', 'bold');

% --- BOTTOM RIGHT: Memory Used ---
subplot(2,2,4);
b4 = bar(algos, mem_data, 'FaceColor', [0.61 0.44 1.00]); % Purple
title('Memory Used (Cost)'); ylabel('Kilobytes (KB)'); grid on;
text(b4.XEndPoints, b4.YEndPoints, string(mem_data), 'HorizontalAlignment','center', 'VerticalAlignment','bottom', 'FontWeight', 'bold');

% 5. Add the Master Title showing BOTH composite scores!
title_text = sprintf('Performance Breakdown for Maze Run ID: %s\nOverall Accuracy Score -> BFS: %.1f%% | DFS: %.1f%%', run_id_name, bfs_score, dfs_score);
sgtitle(title_text, 'FontSize', 14, 'FontWeight', 'bold');