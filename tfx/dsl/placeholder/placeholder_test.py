# Lint as: python3
# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for tfx.dsl.placeholder.placeholder."""

import tensorflow as tf
from tfx.dsl.placeholder import placeholder as ph
from tfx.proto.orchestration import placeholder_pb2

from google.protobuf import text_format


class PlaceholderTest(tf.test.TestCase):

  def _assert_placeholder_pb_equal(self, placeholder, expected_pb_str):
    expected_pb = text_format.Parse(expected_pb_str,
                                    placeholder_pb2.PlaceholderExpression())
    self.assertProtoEquals(placeholder.encode(), expected_pb)

  def testArtifactUriSimple(self):
    self._assert_placeholder_pb_equal(
        ph.input('model').uri, """
        operator {
          artifact_uri_op {
            expression {
              placeholder {
                type: INPUT_ARTIFACT
                key: "model"
              }
            }
          }
        }
    """)

  def testArtifactUriWithIndex(self):
    self._assert_placeholder_pb_equal(
        ph.input('model')[0].uri, """
        operator {
          artifact_uri_op {
            expression {
              operator {
                index_op {
                  expression {
                    placeholder {
                      type: INPUT_ARTIFACT
                      key: "model"
                    }
                  }
                  index: 0
                }
              }
            }
          }
        }
    """)

  def testArtifactSplitUriWithIndex(self):
    self._assert_placeholder_pb_equal(
        ph.input('model')[0].split_uri('train'), """
        operator {
          artifact_uri_op {
            expression {
              operator {
                index_op {
                  expression {
                    placeholder {
                      type: INPUT_ARTIFACT
                      key: "model"
                    }
                  }
                  index: 0
                }
              }
            }
            split: "train"
          }
        }
    """)

  def testPrimitiveArtifactValue(self):
    self._assert_placeholder_pb_equal(
        ph.input('primitive').value, """
        operator {
          artifact_value_op {
            expression {
              placeholder {
                type: INPUT_ARTIFACT
                key: "primitive"
              }
            }
          }
        }
    """)

  def testConcatUriWithString(self):
    self._assert_placeholder_pb_equal(
        ph.output('model').uri + '/model', """
        operator {
          concat_op {
            expressions {
              operator {
                artifact_uri_op {
                  expression {
                    placeholder {
                      type: OUTPUT_ARTIFACT
                      key: "model"
                    }
                  }
                }
              }
            }
            expressions {
              value {
                string_value: "/model"
              }
            }
          }
        }
    """)

  def testExecPropertySimple(self):
    self._assert_placeholder_pb_equal(
        ph.exec_property('num_train_steps'), """
        placeholder {
          type: EXEC_PROPERTY
          key: "num_train_steps"
        }
    """)

  def testExecPropertyProtoField(self):
    self._assert_placeholder_pb_equal(
        ph.exec_property('model_config').num_layers, """
        operator {
          proto_op {
            expression {
              placeholder {
                type: EXEC_PROPERTY
                key: "model_config"
              }
            }
            proto_field_path: "num_layers"
          }
        }
    """)

  def testComplicatedConcat(self):
    self._assert_placeholder_pb_equal(
        ph.output('model').uri + '/model/' + ph.exec_property('version'), """
        operator {
          concat_op {
            expressions {
              operator {
                artifact_uri_op {
                  expression {
                    placeholder {
                      type: OUTPUT_ARTIFACT
                      key: "model"
                    }
                  }
                }
              }
            }
            expressions {
              value {
                string_value: "/model/"
              }
            }
            expressions {
              placeholder {
                type: EXEC_PROPERTY
                key: "version"
              }
            }
          }
        }
    """)


if __name__ == '__main__':
  tf.test.main()
