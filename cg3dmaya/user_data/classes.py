
import cg3dguru.user_data

#class HikMap(cg3dguru.user_data.BaseData):
    
    #@staticmethod
    #def get_suffix():
        #return 'hik'
    
    #@staticmethod
    #def get_attributes():
        
        #child_attrs = [
            #cg3dguru.user_data.create_attr('name', 'string'), 
            #cg3dguru.user_data.create_attr('age', 'long')
        #]
        
        #person : cg3dguru.user_data.Compound = cg3dguru.user_data.create_attr('person', 'compound')
        #for attr in child_attrs:
            #person.add_child(attr)
        
        #attrs = [
            #person, 
            #cg3dguru.user_data.create_attr('test', 'string')
        #]
        
        #return attrs
    
    
    
    
#class DataSamples(cg3dguru.user_data.BaseData):
    #@staticmethod
    #def get_suffix():
        #return ''    
    
    
    #@staticmethod
    #def get_attributes():
        #attrs = []
        #for name in cg3dguru.user_data.Attr.attr_types:
            #attrs.append(cg3dguru.user_data.create_attr('a_' + name, name))
            
        #for name in cg3dguru.user_data.Compound.compound_types:
            #if name == 'compound':
                #continue
            
            #attr = cg3dguru.user_data.create_attr('c_' + name, name)
            #attrs.append(attr)
            
        #return attrs