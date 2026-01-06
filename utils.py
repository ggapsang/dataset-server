import os
import pandas as pd

def get_all_files(root_dir):
    """
    특정 디렉토리의 모든 파일 전체 경로 리스트 가져오기
    
    Args:
        root_dir: 탐색 시작 디렉토리
    
    Returns:
        파일 절대 경로 리스트
    """
    file_list = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.abspath(os.path.join(dirpath, filename))
            file_list.append(file_path)
    
    return file_list


if __name__ == "__main__":
    root_dir = 'data'
    files = get_all_files(root_dir)
    df_files = pd.DataFrame(files, columns=['file_path'])
    df_files.to_csv('data_dir_file_list.csv', index=False)
