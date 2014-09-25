# SRM DB TOOL

Tool to deal with SRM DB

## Main purpose

* Assist GSS/CU/Engineer to deal with SRM DB issue more easily
* Cross Plateform / Cross Database tool

## Language / Tool
* python 2.7 up
* sqlalchemy
* sqlite

# ToDo list

## Phase 1
- [x] Create fake sqlite tables
- [x] Backup Framework / sqlite
- [ ] Configuration Interface - use python structure for now
- [x] Manipulate Recovery Plan
```
   lsrp
   lspg
   rmrp 'rpname' / 'rpmoid'
   rmpg 'rpname' / 'rpmoid'
```

## Phase 2
- [ ] Auto generate table files / list table files / rm table files
```
```
- [ ] standalone lsrp rmrp srmtb(srm table backup) srmrt(srm recover table)
```
srmtb pp/ss tablename sqlite_db_file(default the latest sqlite db)
srmrt pp/ss tablename
```
- [ ] standalone lsrp rmrp srmtb(srm table backup) srmrt(srm recover table)
- [ ] Protection Group (lspg rmpg)


## Phase 3
1. daemonize
2. GUI / Qt
3. As a vApp bundle

