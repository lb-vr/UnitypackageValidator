def hoge():
    try:
        raise Exception("hoge")
    except Exception as e:
        raise e
    finally:
        print("HOGEEEEEEEEEEEEEEEEE")


hoge()
