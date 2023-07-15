
import cg3dguru.user_data as ud

class HikMap(ud.BaseData):
    
    @staticmethod
    def get_suffix():
        return 'hik'
    
    @staticmethod
    def get_attributes():
        attrs = [
            ud.create_attr('test', 'string')
        ]
        
        return attrs