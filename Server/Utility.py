

class Status():

    def __init__(self, status):
        self.state = status

        if(isinstance(status, bool) == False):
            self.state = False

    def set_true(self):
        self.state = True

    def set_false(self):
        self.state = False

    def get(self):
        return self.state

class _id_setter():
    
    def __init__(self, object):
        self.object = object
    
    def name(self, val):
        self.object._name = val
    
    def id(self, val):
        self.object.identifier_token = val

    def expiry_date(self, data):
        self.object.expiration_date = data


class _id_getter():

    def __init__(self, object):
        self.object = object
        pass
    
    def name(self):
        return self.object._name
    
    def id(self):
        return self.object.identifier_token


class _ID():

    def __init__(self, id, name):
        self.identifier_token = id
        self._name = name
        self.expiration_date = None
        self.setter = _id_setter(object=self)
        self.getter = _id_getter(object=self)

    
    def attribute_category(self, cat):
        if(cat == 'getters'):
            return self.getter

        elif(cat == 'setters'):
            return self.setter
        
class ComponentID():
    
    def __init__(self, id, name):
        self.ComponentID = _ID(id, name)
    
    def read(self):
        return self.ComponentID.attribute_category('getters')
    
    def write(self):
        return self.ComponentID.attribute_category('setters')
    
class Atom():
    pass

class Molecule():
    pass

class Receptor():
    pass
