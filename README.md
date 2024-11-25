# EXECUTION STEPS

1. Clone this project in your computer
2. Create environment -> ``conda env create -f GeoInventory.yml``
   1. If any error found, check if you need to change the GeoInventory.yml prefix (last file line)
   2. If you just want to update your current environment: ``conda env update --file GeoInventory.yml``
   3. If you don't even have any conda environment: ``conda create --name <GeoInventory>``
   4. Checkout to the new environment: ``source /home/$(whoami)/anaconda3/bin/activate /home/$(whoami)/env/<GeoInventory>``
3. <span style="color:red"> Check which branch you want to check out </span>
4. <span style="color:red"> Check if you want to connect to testing or production database </span>
5. Execute server: ``python manage.py runserver``
6. If any extra package needed, use ``conda install <package>`` or ``pip install <package>``
7. Update environment file: `conda env export > GeoInventory.yml`

8. <span style="color:red"> Warning: </span> Don't use 'pip freeze > requirements.txt' or 'conda list --explicit > requirements.txt -> you'll mix conda and pip dependencies!
9. If you find some error related to a 'proj.db' file not found, add this in your file:
``os.environ['PROJ_LIB'] = f'{pyproj.datadir.get_data_dir()}'
``