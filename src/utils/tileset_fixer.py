import os
import shutil
import xml.etree.ElementTree as ET
import argparse

def fix_tileset_paths(tmx_file, copy_tilesets=True):
    """
    Исправляет пути к тайлсетам в TMX файле.
    Если copy_tilesets=True, копирует тайлсеты в локальную папку tilesets проекта.
    """
    # Создаем директорию для тайлсетов, если она не существует
    tmx_dir = os.path.dirname(os.path.abspath(tmx_file))
    tilesets_dir = os.path.join(tmx_dir, "tilesets")
    
    if copy_tilesets and not os.path.exists(tilesets_dir):
        os.makedirs(tilesets_dir)
    
    # Парсим TMX файл
    try:
        tree = ET.parse(tmx_file)
        root = tree.getroot()
        
        # Находим все элементы tileset
        tilesets = root.findall(".//tileset")
        
        for tileset in tilesets:
            if "source" in tileset.attrib:
                source_path = tileset.attrib["source"]
                
                # Полный путь к файлу тайлсета относительно TMX
                full_source_path = os.path.normpath(os.path.join(tmx_dir, source_path))
                
                if copy_tilesets and os.path.exists(full_source_path):
                    # Имя файла тайлсета
                    tileset_name = os.path.basename(full_source_path)
                    
                    # Копируем тайлсет в локальную директорию
                    local_tileset_path = os.path.join(tilesets_dir, tileset_name)
                    shutil.copy2(full_source_path, local_tileset_path)
                    
                    # Обновляем путь в TMX
                    new_source_path = os.path.join("tilesets", tileset_name)
                    tileset.attrib["source"] = new_source_path
                    
                    print(f"Скопирован тайлсет: {source_path} -> {new_source_path}")
                    
                    # Теперь нужно также проверить и скопировать изображения из тайлсета
                    # Парсим файл тайлсета
                    try:
                        tsx_tree = ET.parse(full_source_path)
                        tsx_root = tsx_tree.getroot()
                        
                        # Находим изображение в тайлсете
                        image = tsx_root.find("image")
                        if image is not None and "source" in image.attrib:
                            image_path = image.attrib["source"]
                            
                            # Полный путь к изображению относительно TSX
                            full_image_path = os.path.normpath(os.path.join(os.path.dirname(full_source_path), image_path))
                            
                            if os.path.exists(full_image_path):
                                # Имя файла изображения
                                image_name = os.path.basename(full_image_path)
                                
                                # Копируем изображение в локальную директорию
                                local_image_path = os.path.join(tilesets_dir, image_name)
                                shutil.copy2(full_image_path, local_image_path)
                                
                                # Обновляем путь в TSX
                                image.attrib["source"] = image_name
                                
                                # Сохраняем изменения в TSX
                                tsx_tree.write(local_tileset_path)
                                
                                print(f"Скопировано изображение: {image_path} -> {image_name}")
                    except Exception as e:
                        print(f"Ошибка при обработке тайлсета {full_source_path}: {e}")
        
        # Сохраняем изменения в TMX
        tree.write(tmx_file)
        print(f"Файл {tmx_file} успешно обновлен.")
        
    except Exception as e:
        print(f"Ошибка при обработке файла {tmx_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Утилита для исправления путей к тайлсетам в TMX файлах.")
    parser.add_argument("tmx_file", help="Путь к TMX файлу")
    parser.add_argument("--no-copy", action="store_true", help="Не копировать тайлсеты, только обновить пути")
    
    args = parser.parse_args()
    fix_tileset_paths(args.tmx_file, not args.no_copy) 