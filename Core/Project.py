from .FileIO import readYaml,ScanDire,ScanSubDire
from .Library import Library
from .Resource import Resource
from .Templates_Manager import TemplateManager
from .Debug import LogInfo,LogError
import os

class Project:
    def load_plugins(self,plugin_path):
        '''加载插件'''
        for data,name,exten in ScanSubDire(plugin_path,'pack\.yml'):
            dire = os.path.dirname(data['file_path'])
            self.resources.loadResources(f'{dire}\\Resources','')
            
    def import_pack(self,path):
        '''导入资源包'''
        LogInfo(f'[Project] Start to import pack at: {path}')
        pack_info = readYaml(path)
        self.version = pack_info['version']
        LogInfo(f'[Project] Pack version: {self.version}')
        self.base_path = os.path.dirname(path)
        LogInfo(f'[Project] Loading cards')
        self.base_library = Library(readYaml(f"{self.base_path}\\Libraries\\__LIBRARY__.yml"))
        LogInfo(f'[Project] Importing resources')
        self.resources.loadResources(f'{self.base_path}\\Resources','')
        LogInfo(f'[Project] Loading pages')
        for pair in ScanDire(f'{self.base_path}\\Pages',r'.*\.yml$'):
            page:dict = pair[0]
            self.pages.update({ page['name']:page })
            if 'alias' in page:
                for alias in page.get('alias'):
                    self.pages.update({alias:page})
        
    def __init__(self,path):
        LogInfo(f'[Project] Initing ...')
        envpath = os.path.dirname(os.path.dirname(__file__))
        self.resources = Resource()
        LogInfo(f'[Project] Loading basic resources')
        self.resources.loadResources(f'{envpath}\\Resources','')
        LogInfo(f'[Project] Loading plugins')
        self.load_plugins(f'{envpath}\\Plugin')
        self.pages = {}
        self.import_pack(path)
        self.TemplateManager = TemplateManager(self.resources)
        LogInfo(f'[Project] Pack loaded successful!')
    
    def get_page_xaml(self,page_alias):
        '''获取 xaml 代码'''
        LogInfo(f'[Project] Getting codes of page: {page_alias}')
        if page_alias not in self.pages:
            raise KeyError(LogError(f'[Project] Cannot find page named "{page_alias}"'))
        xaml = ''
        for card_ref in self.pages[page_alias]['cards']:
            card_ref = card_ref.replace(' ','').split('|')
            LogInfo(f'[Project] Get card: {card_ref}')
            card = self.base_library.getCard(card_ref[0],False)
            if len(card_ref) > 1:
                for arg in card_ref[1:]:
                    argname,argvalue = arg.split('=')
                    card[argname] = argvalue
            card_xaml = self.TemplateManager.build(card)
            #card_xaml = format_code(card_xaml,card,self.resources.scripts)
            xaml += card_xaml
        return xaml