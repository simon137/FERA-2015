function [geom_data] = Read_geom_files_dynamic(users, vid_ids, hog_data_dir)

    geom_data = [];

    for i=1:numel(users)
        
        geom_file = [hog_data_dir, '/' users{i} '.params.txt'];
        
        res = dlmread(geom_file, ' ');
        res = res(vid_ids(i,1)+1:vid_ids(i,2),15:2:end);       
        
        res = bsxfun(@plus, res, -median(res));
        
        geom_data = cat(1, geom_data, res);
                
    end
end