from util.api_detail import ApiDetail
from util.library_detail import LibraryDetail
from util.package_detail import PackageDetail

tensorflow_detail = LibraryDetail('TensorFlow', 'tensorflow/tensorflow',
                                  [PackageDetail('tensorflow', 'tensorflow')],
                                  ['2', '1'],
                                  [ApiDetail('basic_train_loop', ['tf', 'tensorflow']), ApiDetail('fit', ['tf', 'tensorflow', 'keras', 'tf2']), ApiDetail('fit_generator', ['tf', 'tensorflow', 'keras', 'tf2']), ApiDetail('train_on_batch', ['tf', 'tensorflow', 'keras', 'tf2'])],
                                  [ApiDetail('load', ['tf', 'tensorflow', 'tf2', 'tensorflow_hub']), ApiDetail('load_model', ['tf', 'tensorflow', 'keras', 'tf2']), ApiDetail('load_v2', ['tf', 'tensorflow']), ApiDetail('load_weights', ['tf', 'keras'])])
pytorch_detail = LibraryDetail('PyTorch', 'pytorch/pytorch',
                               [PackageDetail('torch', 'torch')],
                               ['2', '1'],
                               [ApiDetail('Module', ['torch'], 'class'), ApiDetail('nn.Module', ['torch'], 'class'), ApiDetail('Sequential', ['torch'], 'class'), ApiDetail('nn.Sequential', ['torch'], 'class')],
                               [ApiDetail('load', ['torch']), ApiDetail('load_state_dict', ['torch'])])
scikit_learn_detail = LibraryDetail('scikit-learn', 'scikit-learn/scikit-learn',
                                    [PackageDetail('scikit-learn', 'scikit-learn'), PackageDetail('sklearn', 'scikit-learn')],
                                    ['1', '0'],
                                    [ApiDetail('fit', ['sklearn']), ApiDetail('fit_predict', ['sklearn']), ApiDetail('fit_transform', ['sklearn']), ApiDetail('partial_fit', ['sklearn'])],
                                    [ApiDetail('loads', ['pickle']), ApiDetail('load', ['joblib', 'pickle'])])

LIBRARIES = {
    'tensorflow': tensorflow_detail,
    'pytorch': pytorch_detail,
    'scikit-learn': scikit_learn_detail
}

METHOD_NAMES = []
CLASS_NAMES = []
for library_short_name, library_detail in LIBRARIES.items():
    for api in library_detail.training_apis:
        if api.is_api_type_method():
            METHOD_NAMES.append(api.api_name)
        elif api.is_api_type_class():
            CLASS_NAMES.append(api.api_name)
    for api in library_detail.model_loading_apis:
        if api.is_api_type_method():
            METHOD_NAMES.append(api.api_name)
        elif api.is_api_type_class():
            CLASS_NAMES.append(api.api_name)
