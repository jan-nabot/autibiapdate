#!/usr/bin/env python
__author__ = 'github.com/user/jan-nabot/'
__version__ = '1.0'
from os import listdir, access, R_OK, F_OK, W_OK
from sys import argv, version_info, stdout
from shutil import copytree
from tarfile import open as extracttargz

urlname = 'http://download.tibia.com/tibia.x64.tar.gz'
tarname = 'tibia.x64.tar.gz'
filesofinterest = ('minimap', 'conf', 'characterdata')
warned = 0


def main():
    '''This program scripts away hassle of manually updating Tibia client for Linux.'''
    if '--help' in argv or '-h' in argv:
        print('Run this program with Python interpreter of your choice '
              'from directory containing at least one obsolete version of Tibia '
              'to automatically download newest client and copy your settings, '
              'hotkeys, minimap files to new location')
        return 1
    else:
        fromdir = findinstallments(True)
        stdout.write('Downloading...')
        deployclient()
        todir = findinstallments(False)
        assert todir[1] > fromdir[1], 'New client deployment failed.'
        print('\nDeployment done, time to migrate user data.')
        print(fromdir[0] + ' --> ' + todir[0])
        migrate(fromdir[0], todir[0])
        print('Migration done.')
        print('Done.')
        return 0


def deployclient():
    '''Download and extract new Tibia version.'''
    def extractclient():
        '''Unpack client from .tar.gz archive.'''
        eh = extracttargz(tarname)
        eh.extractall()
        eh.close()
    if version_info.major == 3:
        from urllib.request import urlopen as getit
    else:
        from urllib import urlopen as getit
    global tarname
    if access(tarname, F_OK):  # avoid overwriting client archive if it was'nt downloaded by this program
        tarname = 'disposable' + tarname
    if access('.', W_OK) is not True:
        raise IOError(
            "You don't have permissions to create file here. Suggested action "
            "is to get proper permissions to this directory or optionally run "
            "this program with sudo.")
    with open(tarname, 'wb') as memtofile:
        tomemdl = getit(urlname)
        while True:
            data = tomemdl.read(555555) 
            if not data:
                break
            else:
                memtofile.write(data)
                stdout.write('.')  # download progress indicator
                stdout.flush()
    extractclient()
    return 0


def findinstallments(predownload):
    '''Detect client versions and choose most recent with settings and minimap saved.'''
    global warned
    curdirlist = listdir('.')
    dirsfound = []
    for dirname in curdirlist:
        if dirname.startswith('tibia-'):
            try:
                dirsfound.append((dirname, int(dirname[6:16].replace('.', ''))))
            except ValueError:
                if warned == 0:
                    print('Unable to parse version from dirname.')
                    raise Warning('Unable to parse version number from directory name.')
                    warned = 1
    if len(dirsfound) == 0:
        raise LookupError('No Tibia installations found in current directory.')

    dirsfound.sort(key=lambda x: int(x[1]), reverse=True)  # sort by version

    if predownload:
        for dirtuple in dirsfound:
            if all(x in listdir(dirtuple[0]) for x in filesofinterest):
                for confile in filesofinterest:  # confirm user has enough permissions for migrated files
                    checkit = dirtuple[0] + '/' + confile
                    assert access(checkit, R_OK), (
                        'You dont have enough permissions to copy minimap '
                        'or settings. Suggested action is to change permissions to: '
                        + checkit + ' or run this program with sudo')
                return dirtuple
        raise LookupError('Full set of settings and/or minimap not found. Aborting.')

    elif predownload is False:  # if program is used as intended below assert should never trigger
        assert any(x in filesofinterest for x in listdir(dirsfound[0][0])) is False, (
            'There already are minimap or config files in directory of newest version, '
            'overwriting them couldbe bad idea. Aborting.')
        return dirsfound[0]


def migrate(sourcedir, destdir):
    '''Copy settings and minimap from older to current client version.'''
    ndircheck = listdir(destdir)

    assert any(x in filesofinterest for x in ndircheck) is False, (
        'There already are minimap or config files '
        'in directory of newest version, overwriting them could be bad idea.  Aborting.')

    mmsrc, confsrc, chardatsrc = (sourcedir + '/' + trail for trail in filesofinterest)  # create pathnames
    mmdst, confdst, chardatdst = (destdir + '/' + trail for trail in filesofinterest)  # create pathnames

    copytree(mmsrc, mmdst)
    copytree(confsrc, confdst)
    copytree(chardatsrc, chardatdst)
    return 0


main()
