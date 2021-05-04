import unittest
import edgefarm.avro as avro
import edgefarm.schema as schema


class TestAvro(unittest.TestCase):

    def test_avro_ping_pong(self):
        msg = [
            {u'topic': "myfancytopic"}
        ]
        w = avro.new_writer(msg, schema.register_sub_request_codec)

        r = avro.new_reader(w)
        self.assertEqual(r["topic"], "myfancytopic")


if __name__ == '__main__':
    unittest.main()
