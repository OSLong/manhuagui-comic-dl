import enum


class CHAPTER_TYPE(enum.Enum):
    UNDEFINED = 'Undefined'
    VOLUME = '单行本'
    EPISODE = '单话'
    EXTRA = '番外篇'

    @classmethod
    def _get_chapter_type_from_chinese(cls, chinese_name):
        if chinese_name in ['番外篇']:
            return CHAPTER_TYPE.EXTRA
        elif chinese_name in ['单行本', '單行本' ]:
            return CHAPTER_TYPE.VOLUME
        elif chinese_name in ['单话', '單話']:
            return CHAPTER_TYPE.EPISODE
        else:
            pass
        return CHAPTER_TYPE.UNDEFINED