# import datetime
# from textual import log
# from textual.app import App, ComposeResult
# from textual.widgets import Footer, Header, ListView, Button, Static, ListItem, Label
# from textual.containers import Horizontal, Vertical, HorizontalGroup
# from textual.reactive import reactive
# from textual.widget import Widget

# from .ebook_merger_service import EbookMergerService

# import traceback

# class EPubUnTransferItems(Widget):
#     # epub_item = reactive({})

#     def __init__(self, epub_item,):
#         self.epub_item = epub_item
#         return super().__init__()

    
#     # def render(self):
#     #     log("Epub Under rc0mopsoe ", self.epub_item)
#     #     item = self.epub_item
#     #     return Label("Hello World")
#     #     return Horizontal(
#     #         Label(
#     #             item['name']
#     #         ),
#     #         Button(
#     #             '>>'
#     #         )
#     #     )
#     def compose(self):
#         yield Label("WOrld Hello")
        
    

# class EbookMergerApp(App):
#     """A Textual app to manage stopwatches."""
#     CSS_PATH = './ebook_merger_style.tcss'


    
#     all_items = reactive([], recompose=True)
#     selected_items = reactive([], recompose=True)

#     def __init__(self, opts, *args, **kwargs):
#         res = super(EbookMergerApp, self).__init__(*args, **kwargs)
#         self.opts = opts
#         self.service = EbookMergerService(opts=opts)
#         return res
    
#     def _fatal_error(self) -> None:
#         log("Got Fatal Eeeeeeeeeeeeeeeeee11111 2222=====================", traceback.format_exc())

#         super()._fatal_error()
#         _, exception, _ = sys.exc_info()

#         if exception is not None:
#             raise exception
        
#     # BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]\
#     def on_mount(self):   
#         log(f"serservice ",self.service)
#         # try:

#         epub_files = self.service._list_epub_in_directory()
#         self.all_items = epub_files
#         self.mutate_reactive(EbookMergerApp.all_items)
#         for list_item in self.query(ListItem):
#             list_item.recompose()
#         pass
    

#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         """Event handler called when a button is pressed."""
       
#         pass

#     def compose(self) -> ComposeResult:
#         """Create child widgets for the app."""
#         # print("Run Compose ")


#         unselected_list_items = [
#             ListItem(
#                 EPubUnTransferItems(epub_item=epub_item),
#                 # Label("My Label")
                
#             )
#             for epub_item in self.all_items
#             # if epub_item not in self.selected_items
#         ]
#         log("Unsele ce item ", unselected_list_items)

#         yield Header()

#         yield Horizontal(
#             ListView(
#                 ListItem(
#                     Label("Found EPUBs.", ),
#                     disabled=True,
#                     classes='text-center'
#                 ),
#                 *unselected_list_items,
#                 classes='columns',
#             ),

#             ListView(
#                 ListItem(
#                     Label("Merge EPUbs.",),
#                     disabled=True,
#                     classes='text-center'
#                 ),
#                 classes='columns'
#             )
#         )

        

#         yield Footer()


# # def main():
# #     pass

# # if __name__ == '__main__':
# #     start_time = datetime.datetime.now()
# #     print('Start at : ', str(start_time))

# #     main()
    
# #     end_time = datetime.datetime.now()
# #     print("End at : ", str(end_time))
# #     print("Elapsed : ", str(end_time - start_time))