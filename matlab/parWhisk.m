function [Status,WhiskerFiles,MeasurementFiles] = parWhisk(Files,N,varargin)
% PARWHISK parallelizes Nathan Clack's whisk toolbox
%
% STATUS = PARWHISK(FILES,N) runs Clack's trace, measure, classify, &
% reclassify on all filenames input in FILES. FILES

% Default parameters that can be adjusted
Ext = '*.tif';        % extension of files to pull out of directories input
faceStr = '13 450 y'; % location of mouse's face: 'x y axis' (see: measure --help)
px2mm = 0.014;        % length of a pixel in millimeters (see: classify --help)
directory = pwd;      % default directory when prompting user to select a file

%% Parse input arguments
index = 1;
while index<=length(varargin)
    try
        switch varargin{index}
            case {'ext','Ext','e'}
                Ext = varargin{index+1};
                index = index + 2;
            case {'face','Face'}
                faceStr = varargin{index+1};
                index = index + 2;
            case 'px2mm'
                px2mm = varargin{index+1};
                index = index + 2;
            otherwise
                warning('Argument ''%s'' not recognized',varargin{index});
                index = index + 1;
        end
    catch
        warning('Argument %d not recognized',index);
        index = index + 1;
    end
end

% Determine files to analyze
if ~exist('Files','var') || isempty(Files)
    Files = uigetdir(directory,'Select directory to analyze');
    if isnumeric(Files)
        return
    end
end
if ischar(Files)
    Files = {Files};
end
numIn = numel(Files);

% Make sure # of N input equals # of files input
if ~exist('N','var') || isempty(N)
    N = 0;
end
if numel(N)==1 && numIn>1
    N = repmat(N,numIn,1);
elseif numel(N)~=numIn
    error('# of elements in second input must equal 1 or number of directories input');
end


%% Ensure the binaries are on the path
[test,~] = system('trace'); % should return 1
if test==127
    error('whisk binaries are not found on PATH.');
end


%% Identify files in directories input
if isrow(Files)
    Files = Files';
end
if isrow(N)
    N = N';
end
for f = numIn:-1:1
    if isdir(Files{f})
        temp = dir(fullfile(Files{f},Ext));
        temp = fullfile(Files{f},{temp(:).name})';
        n = numel(temp);
        Files = cat(1,Files,temp);
        N = cat(1,N,repmat(N(f),n,1));
        Files(f) = [];
        N(f) = [];
    end
end
numIn = numel(Files);


%% Process files
Status = ones(numIn,4);
n = strfind(flip(Files{1}),'.')-1; % find extension length
WhiskerFiles = cellfun(@(x) [x(1:end-n),'whiskers'],Files,'UniformOutput',false);
MeasurementFiles = cellfun(@(x) [x(1:end-n),'measurements'],Files,'UniformOutput',false);
parfor f = 1:numIn
    status = ones(1,4);
    
    [status(1),~] = system(['trace ' Files{f} ' ' WhiskerFiles{f}]);
    
    [status(2),~] = system(['measure --face ' faceStr ' ' WhiskerFiles{f} ' ' MeasurementFiles{f}]);
    
    [status(3),~] = system(['classify ' MeasurementFiles{f} ' '...
        MeasurementFiles{f} ' ' faceStr ' --px2mm ' num2str(px2mm) ' -n ' num2str(N(f))]);
    
    [status(4),~] = system(['reclassify ' MeasurementFiles{f} ' '...
        MeasurementFiles{f} ' -n ' num2str(N(f))]);
    
    Status(f,:) = status;
end

