from dokigo import base
import tempfile
import h5py
from tensorflow.keras.models import load_model
from dokigo.encoders.base import get_encoder_by_name
COLS = 'ABCDEFGHJKLMNOPQRST'

STONE_TO_CHAR = {
    None:' . ',
    base.Player.black: ' x ',
    base.Player.white: ' o '
}

def print_move(player, move):
    if move.is_pass:
        move_str = 'passes'
    elif move.is_resign:
        move_str = 'resigns'
    else:
        move_str = '%s%d' % (COLS[move.point.col-1], move.point.row)
    print('%s %s' % (player, move_str))


def print_board(board):
    for row in range(board.num_rows,0,-1):
        bump = ' ' if row <=9 else ''
        line = []
        for col in range(1,board.num_cols+1):
            stone = board.get(base.Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump,row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.num_cols]))


def point_from_coords(coords):
    col = COLS.index(coords[0])+1
    row = int(coords[1:])
    return base.Point(row=row, col=col)


def coords_from_point(point):
    return '%s%d'%(COLS[point.col-1], point.row)


def save_nn_model(h5file_name, model, encoder):
    with h5py.File(h5file_name,'w') as h5file:
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = encoder.name()
        h5file['encoder'].attrs['board_width'] = encoder.board_width
        h5file['encoder'].attrs['board_height'] = encoder.board_height
        h5file.create_group('model')
        with tempfile.NamedTemporaryFile() as f:
            model.save(f.name, save_format='h5')
            serialized_model = h5py.File(f.name, 'r')
            root_item = serialized_model.get('/')
            serialized_model.copy(root_item, h5file['model'], 'kerasmodel')

def load_nn_model(h5file_name):
    with h5py.File(h5file_name,'r') as h5file:
        with tempfile.NamedTemporaryFile() as f:
            serialized_model = h5py.File(f.name, 'w')
            root_item = h5file.get('model/kerasmodel')
            for attr_name, attr_value in root_item.attrs.items():#todo check if there is a simpler way
                serialized_model.attrs[attr_name] = attr_value
            for k in root_item.keys():
                h5file.copy(root_item.get(k), serialized_model, k)
            model = load_model(f.name)

        encoder_name = h5file['encoder'].attrs['name']
        if not isinstance(encoder_name, str):
            encoder_name = encoder_name.decode('ascii')
        board_width = h5file['encoder'].attrs['board_width']
        board_height = h5file['encoder'].attrs['board_height']
        encoder = get_encoder_by_name(
            encoder_name, (board_width,board_height))
    return model, encoder