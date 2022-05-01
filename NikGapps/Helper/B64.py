import base64


class B64:

    @staticmethod
    def b64e(s):
        return base64.b64encode(s.encode()).decode()

    @staticmethod
    def b64d(s):
        try:
            val = base64.b64decode(s).decode()
        except Exception as e:
            print(str(e))
            return s
        return val

    @staticmethod
    def is_base64(sb):
        try:
            if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the function will return false
                sb_bytes = bytes(sb, 'ascii')
            elif isinstance(sb, bytes):
                sb_bytes = sb
            else:
                raise ValueError("Argument must be string or bytes")
            return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception as e:
            print(str(e))
            return False
