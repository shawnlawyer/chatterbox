class BaseController:

    def feature(self, feature, **kwargs):

        view = None
        model = self.model(**kwargs)
        try:
            view = self.view.feature(model, feature)
        except:
            pass

        return view

    def detail(self, **kwargs):

        view = None
        model = self.model(**kwargs)
        try:
            view = self.view.detail(model)
        except:
            pass

        return view

    def next(self):
        return self.search_result(direction='next')

    def previous(self):
        return self.search_result(direction='previous')

    @property
    def current_id(self):
        id = None
        if self.search_ids and self.search_ids_current_id_index != None:
            id = list(self.search_ids)[self.search_ids_current_id_index]

        return id

    def clear_search_results(self):

        self.session.pop(self.session_keys['CONTEXT'])
        self.session.pop(self.session_keys['SEARCH_IDS'])
        self.session.pop(self.session_keys['SEARCH_CURRENT_INDEX'])


    def set_search_results(self, results):

        self.session.set('CONTEXT', self.session_keys['CONTEXT'])
        self.session.set(self.session_keys['SEARCH_IDS'], results)
        self.session.set(self.session_keys['SEARCH_CURRENT_INDEX'], 0)

    @property
    def search_ids(self):
        if self.session.has(self.session_keys['SEARCH_IDS']):
            return self.session.get(self.session_keys['SEARCH_IDS'])

        return None

    @property
    def search_ids_current_id_index(self):
        if self.session.has(self.session_keys['SEARCH_CURRENT_INDEX']):
            return self.session.get(self.session_keys['SEARCH_CURRENT_INDEX'])

        return None

    def set_search_ids_current_id_index(self, index):
        self.session.set(self.session_keys['SEARCH_CURRENT_INDEX'], index)
        return None
