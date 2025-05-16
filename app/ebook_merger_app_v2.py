from textual.app import App
import textual.events
from textual.widgets import Label, Button, ListView, ListItem, Header, Footer, Input
from textual.containers import Horizontal, Vertical, Center
from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive

import textual

import traceback
import sys
import os

from . import ebook_merger_service



class FoundSideListItem(Widget):
    DEFAULT_CSS = """
        FoundSideListItem {
            height: auto
        }
        FoundSideListItem Horizontal {
            height: auto
        }
        FoundSideListItem Label {
            width: 1fr
        }
        FoundSideListItem Button {
            padding: 0
        }
    """

    class MoveRight(Message):
        def __init__(self, item):
            super().__init__()
            self.item = item

    def set_data(self, item):
        self.item = item
        return self
    

    @textual.on(Button.Pressed, '#button-archived')
    def action_archived(self):
        self.styles.height = 0

    def action_unarchive(self):
        self.styles.height = 'auto'

    def action_hide(self):
        self.styles.display = 'none'

    def action_show(self):
        self.styles.display = 'block'

    @textual.on(Button.Pressed, '#button-move-right')
    def action_move_right(self):
        self.action_hide()
        self.post_message(self.MoveRight(self.item))
        pass


    def compose(self):
        item = self.item
        label = item['name']
        sequence = item['sequence']

        yield Horizontal(
            Label(label),
            Label(sequence),
            Button(
                '>>',
                id='button-move-right'
            ),
            Button(
                'Archived',
                id='button-archived'
            )
        )

class SelectedSideListItem(Widget):
    DEFAULT_CSS = """
        SelectedSideListItem {
            height: auto
        }
        SelectedSideListItem Horizontal {
            height: auto
        }
        SelectedSideListItem Label {
            width: 1fr
        }
        SelectedSideListItem Button {
            padding: 0
        }
    """
    class MoveLeft(Message):
        def __init__(self, item):
            super().__init__()
            self.item = item

    class Reorder(Message):
        def __init__(self, widget, direction: int,):
            super().__init__()
            self.direction = direction
            self.widget = widget
    
    def set_data(self, item):
        self.item = item
        return self
    
    @textual.on(Button.Pressed, '#button-move-up')
    def action_move_up(self):
        self.post_message(self.Reorder(self, -1))
        pass

    @textual.on(Button.Pressed, '#button-move-down')
    def action_move_down(self): 
        self.post_message(self.Reorder(self, 1))
        pass


    @textual.on(Button.Pressed, '#button-move-left')
    def action_move_left(self):
        self.post_message(self.MoveLeft(self.item))
        self.parent.remove()
        self.log("View Remove Parent ", )
        pass

    
    def compose(self):
        item = self.item
        label = item['name']
        yield Horizontal(
            Label(label),
            Button(
                'UP',
                id='button-move-up'
            ),
            Button(
                'Down',
                id='button-move-down'
            ),
            Button(
                '<<',
                id='button-move-left'
            ),
        )

class MergeInputArea(Widget):
    DEFAULT_CSS = """
        MergeInputArea {
            height: auto
        }
       
    """
    
    def set_export_book_name(self, name):
        self.export_name_input.value = name

    def get_export_book_name(self):
        return self.export_name_input.value

    # @textual.on(Button.Pressed, '#button-generate-name')
    # def on_button_generate_name_clicked(self, event: Button.Pressed):
    #     main_app: EbookMergerAppV2 = self.parent.parent
    #     # self.log("View Generat Nam " , self, self.parent, self.parent.parent)
    #     self.export_book_name = main_app.get_first_item_name()

    def compose(self):
        self.export_name_input = Input(
                placeholder='Merge File Name',
                id='merge-input-file-name',
                classes='merge-input-file-name',
        )
        yield Horizontal(
            self.export_name_input,
            
            Button(
                "Merge",
                classes='button-merged',
                id='button-merged'
            ),
            classes='merge-container',
        )

class EbookMergerAppV2(App):
    title = 'E-Book Merger V2'
    CSS_PATH = './ebook_merger_style.tcss'

    def __init__(self, opts, driver_class = None, css_path = None, watch_css = False, ansi_color = False):
        super().__init__(driver_class, css_path, watch_css, ansi_color)
        self.opts = opts
        self.ebook_service = ebook_merger_service.EbookMergerService(opts)

    def build_left_side_list_item(self, item):
        return ListItem(
            FoundSideListItem(id=item['id']).set_data(item),
        )
    
    def build_right_side_list_item(self, item):
        return ListItem(
            SelectedSideListItem(id=item['id']).set_data(item),
        )
    
    @textual.on(FoundSideListItem.MoveRight)
    def on_select(self, event: FoundSideListItem.MoveRight):
        selected_item = event.item
        right_list_item = self.build_right_side_list_item(selected_item)
        self.right_list_view.mount(right_list_item)

        if not self.merged_input_area.get_export_book_name():
            self.merged_input_area.set_export_book_name( selected_item['name'])

    @textual.on(SelectedSideListItem.MoveLeft)
    def on_unselect(self, event: SelectedSideListItem.MoveLeft):
        selected_item = event.item
        id = selected_item['id']
        left_side_item: FoundSideListItem = self.left_list_view.query_one(f"#{id}")
        left_side_item.action_show()

    def _get_right_list_view_selected_list_items(self):
        children = self.right_list_view.query('SelectedSideListItem').nodes
        return children
    
    def _find_widget_index(self, widget):
        children = self._get_right_list_view_selected_list_items()
        return next(( i for i, w in enumerate(children) if w == widget ), -1)

    @textual.on(SelectedSideListItem.Reorder)
    def on_reorder(self, event : SelectedSideListItem.Reorder):
        widget = event.widget
        widget_index = self._find_widget_index(widget)
        
        right_list_selected_list_items = self._get_right_list_view_selected_list_items()
        max_children = len(right_list_selected_list_items)
        target_index = widget_index + event.direction
        
        valid_range = 0 <= target_index < max_children 
        if not valid_range:
            return 

        if event.direction == -1:
            self.right_list_view.move_child(child=widget_index, before=widget_index - 1)
        if event.direction == 1:
            self.right_list_view.move_child(child=widget_index, after=widget_index + 1)



    def on_mount(self):
        epub_files = self.ebook_service._list_epub_in_directory()
        data = [
            {
                'id': f'id-{index + 1}',
                **item
            }
            for index , item in enumerate(epub_files)
        ]
        
        left_side_list_items = [
            self.build_left_side_list_item(item)
            for item in data
        ]
        self.left_list_view.extend(left_side_list_items)

        # for item in data[4:7]:
        #     list_item: FoundSideListItem = self.build_right_side_list_item(item)
        #     # list_item.action_move_right()
        #     self.right_list_view.mount(list_item)
        # pass

    def get_first_item_name(self):
        selected_side_list_items = self.right_list_view.query('SelectedSideListItem').nodes

        if not selected_side_list_items:
            return ''
        
        first_right_list_item = selected_side_list_items[0]
        
        return first_right_list_item.item.get('name') or ''

    @textual.on(Button.Pressed, '#button-merged')
    def on_button_merged_clicked(self, event: Button.Pressed):
        button = event.button
        button.loading = True
        button.disabled = True

        selected_list_items: list[SelectedSideListItem] = self.right_list_view.query("SelectedSideListItem").nodes
        items = [
            select_list_item.item
            for select_list_item in selected_list_items
        ]

        self.log("Selected is ", items)

        output_dir = self.opts.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        book_name = self.merged_input_area.get_export_book_name()

        output_path = f'{output_dir}/{book_name}.epub'

        self.log("Output Path is : ", output_path)

        to_merged_file_paths = [ item['path'] for item in items]

        self.ebook_service._merge_epub_files(output_path, to_merged_file_paths)

        # close after finished
        sys.exit(0)
        pass

    @textual.on(ListView.Highlighted)
    def on_selected_list_view_changed(self, evt):
        self.log("Run Change LKist View changed ", evt)

    def compose(self):
        self.left_list_view = ListView()
        self.right_list_view = ListView()

        self.merged_input_area = MergeInputArea()

        yield Header()

        yield Vertical(
            Horizontal(
                Vertical(
                    Center(
                        Label("Found EPUB Files"),
                    ),
                    self.left_list_view,
                    classes='columns'
                ),
                Vertical(
                    Center(
                        Label("Selected EPUB Files"),
                    ),
                    self.right_list_view,
                    classes='columns'
                )
            ),   
        )
        yield self.merged_input_area 

        yield Footer()

    def _fatal_error(self) -> None:
        self.log("Got Error =====================", traceback.format_exc())

        super()._fatal_error()
        _, exception, _ = sys.exc_info()

        if exception is not None:
            raise exception
        
if __name__ == '__main__':
    import argparse
    from cli.ebook_merger import _init_parser
    args = sys.argv

    parser = argparse.ArgumentParser()
    _init_parser(parser=parser)
    opts = parser.parse_args(args=args)

    app = EbookMergerAppV2(opts)

    app.run()